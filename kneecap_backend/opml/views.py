from django.shortcuts import render
import xml.etree.ElementTree as ET
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rss.models import RSSFeed

class OPMLImportView(APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        opml_file = request.FILES['file']
        
        if not opml_file.name.endswith('.opml'):
            return Response({'error': 'File must be an OPML file'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            tree = ET.parse(opml_file)
            root = tree.getroot()
            
            # Find all outline elements with xmlUrl attribute (RSS feeds)
            feeds = []
            for outline in root.findall('.//outline[@xmlUrl]'):
                link = outline.get('xmlUrl')
                
                # Create or get the feed
                feed, created = RSSFeed.objects.get_or_create(
                    link=link,
                )
                feeds.append({
                    'link': link,
                })

            return Response({
                'feeds': feeds
            })

        except ET.ParseError:
            return Response({'error': 'Invalid OPML file'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
