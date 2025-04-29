from defusedxml import ElementTree as DefusedET
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rss.models import RSSSubscription
import logging
import time
import io

logger = logging.getLogger(__name__)


class OPMLImportView(APIView):
    parser_classes = (MultiPartParser,)

    def try_create_feed(self, link):
        try:
            if RSSSubscription.objects.filter(link=link).exists():
                return {"success": True, "created": False, "error": None}
            RSSSubscription.objects.create(link=link)
            return {"success": True, "created": True, "error": None}
        except Exception as e:
            error_msg = str(e)
            # logger.error(f"Failed to create feed {link}: {error_msg}")
            return {"success": False, "created": False, "error": error_msg}

    def post(self, request):
        if "file" not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        opml_file = request.FILES["file"]
        max_size = 5 * 1024 * 1024
        if opml_file.size > max_size:
            return Response(
                {"error": "OPML file exceeds 5MB size limit"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            file_bytes = opml_file.read()
            tree = DefusedET.parse(io.BytesIO(file_bytes))
            root = tree.getroot()
            feeds_results = []
            failed_feeds = []
            success_count = 0
            failure_count = 0
            outlines = root.findall(".//outline[@xmlUrl]")
            total = len(outlines)
            logger.info(f"[OPML Import] Starting import of {total} feeds...")
            for idx, outline in enumerate(outlines, 1):
                logger.info(f"[OPML Import] Processing feed {idx}/{total}: {outline.get('xmlUrl')}")
                feed_result = {
                    "link": outline.get("xmlUrl"),
                    "title": outline.get("title", ""),
                    "status": "success",
                    "error": None,
                }
                result = self.try_create_feed(outline.get("xmlUrl"))
                if result["success"]:
                    if result["created"]:
                        success_count += 1
                        logger.info(f"[OPML Import] Successfully created: {outline.get('xmlUrl')}")
                    else:
                        logger.info(f"[OPML Import] Feed already exists: {outline.get('xmlUrl')}")
                else:
                    failure_count += 1
                    feed_result["status"] = "error"
                    feed_result["error"] = result["error"]
                    failed_feeds.append(feed_result)
                    logger.error(f"[OPML Import] Failed to create: {outline.get('xmlUrl')} | Error: {result['error']}")
                feeds_results.append(feed_result)
                if idx % 10 == 0 or idx == total:
                    logger.info(f"[OPML Import] Progress: {idx}/{total} feeds processed...")
            logger.info(f"[OPML Import] Import complete: {success_count} succeeded, {failure_count} failed.")
            if failed_feeds:
                logger.info(f"Retrying {len(failed_feeds)} failed feeds...")
                for failed_feed in failed_feeds:
                    time.sleep(10)
                    result = self.try_create_feed(failed_feed["link"])
                    for feed in feeds_results:
                        if feed["link"] == failed_feed["link"]:
                            if result["success"]:
                                feed["status"] = "success"
                                feed["error"] = None
                                feed["created"] = result["created"]
                                success_count += 1
                                failure_count -= 1
                            break
            return Response(
                {
                    "summary": {
                        "total": len(feeds_results),
                        "successful": success_count,
                        "failed": failure_count,
                    },
                    "feeds": feeds_results,
                }
            )
        except DefusedET.ParseError:
            return Response({"error": "Invalid OPML file"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"OPML import failed: {str(e)}")
            return Response(
                {"error": "An internal Error Occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
