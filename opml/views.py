import xml.etree.ElementTree as ET
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rss.models import RSSSubscription
import logging
import time

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
            logger.error(f"Failed to create feed {link}: {error_msg}")
            return {"success": False, "created": False, "error": error_msg}

    def post(self, request):
        if "file" not in request.FILES:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        opml_file = request.FILES["file"]
        if not opml_file.name.endswith(".opml"):
            return Response(
                {"error": "File must be an OPML file"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            tree = ET.parse(opml_file)
            root = tree.getroot()
            feeds_results = []
            failed_feeds = []
            success_count = 0
            failure_count = 0
            for outline in root.findall(".//outline[@xmlUrl]"):
                feed_result = {
                    "link": outline.get("xmlUrl"),
                    "title": outline.get("title", ""),
                    "status": "success",
                    "error": None,
                }
                result = self.try_create_feed(feed_result["link"])
                if result["success"]:
                    feed_result["created"] = result["created"]
                    success_count += 1
                else:
                    feed_result["status"] = "failed"
                    feed_result["error"] = result["error"]
                    failure_count += 1
                    failed_feeds.append(feed_result)
                feeds_results.append(feed_result)
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
        except ET.ParseError:
            return Response({"error": "Invalid OPML file"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"OPML import failed: {str(e)}")
            return Response({"error": "An internal error has occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
