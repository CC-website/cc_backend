@method_decorator(csrf_exempt, name='dispatch')
class SubChannelView(View):

    def get(self, request, subchannel_id=None):
        if subchannel_id:
            subchannel = get_object_or_404(SubChannel, pk=subchannel_id)
            data = model_to_dict(subchannel)
        else:
            subchannels = SubChannel.objects.all()
            data = serializers.serialize('json', subchannels)
        return JsonResponse(data, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body)
            channel_id = data.get('channel_id', '')
            name = data.get('name', '')
            description = data.get('description', '')
            print(name)
            print(description)
            print(channel_id)
            
            # Now, you can process the data and save it to the database using a serializer
            serializer = SubChannelSerializer(data={'channel':channel_id, 'name': name, 'description': description})
            
            if serializer.is_valid():
                serializer.save()
                print(serializer.data)
                return JsonResponse(serializer.data, status=201)
            print('Nigel')
            return JsonResponse(serializer.errors, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    def put(self, request, subchannel_id):
        try:
            # Fetch the existing channel
            channel = SubChannel.objects.get(pk=subchannel_id)

            data = json.loads(request.body)
            name = data.get('name', None)
            description = data.get('description', None)

            # Update channel data if non-empty and non-null
            if name is not None:
                channel.name = name
            if description is not None:
                channel.description = description

            channel.save()

            # Return updated channel data
            serializer = SubChannelSerializer(channel)
            return JsonResponse(serializer.data, status=200)

        except SubChannel.DoesNotExist:
            return JsonResponse({'error': 'Channel not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    def delete(self, request, subchannel_id):
        try:
            # Fetch the existing channel
            channel = SubChannel.objects.filter(id=subchannel_id).first()
            print(channel.name)
            channel.delete()
            return JsonResponse({'message': 'Channel deleted successfully'}, status=200)
        except SubChannel.DoesNotExist:
            return JsonResponse({'error': 'Channel not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class GroupView(View):
    def get(self, request, group_id=None):
        if group_id:
            group = get_object_or_404(Group, pk=group_id)
            data = model_to_dict(group)
        else:
            groups = Group.objects.all()
            data = serializers.serialize('json', groups)
        return JsonResponse(data, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body)
            subchannel_id = data.get('subchannel', '')
            name = data.get('name', '')
            description = data.get('description', '')
            image_base64 = data.get('image', '')

            # Initialize image_data with None
            image_data = None

            # Decode base64 image data
            if image_base64 and ';base64,' in image_base64:
                format, imgstr = image_base64.split(';base64,')  # Extract the format and base64 part
                ext = format.split('/')[-1]  # Extract the image extension
                image_data = ContentFile(base64.b64decode(imgstr), name=f"{name}_logo.{ext}")

            # Now, you can process the data and save it to the database using a serializer
            serializer = SubGroupSerializer(data={'subchannel':subchannel_id, 'name': name, 'description': description, 'logo': image_data})
            
            if serializer.is_valid():
                serializer.save()
                print(serializer.data)
                return JsonResponse(serializer.data, status=201)
            print('Nigel')
            return JsonResponse(serializer.errors, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)


    def put(self, request, group_id):
        try:
            # Fetch the existing channel
            channel = Group.objects.get(pk=group_id)

            data = json.loads(request.body)
            name = data.get('name', None)
            description = data.get('description', None)

            # Update channel data if non-empty and non-null
            if name is not None:
                channel.name = name
            if description is not None:
                channel.description = description

            channel.save()

            # Return updated channel data
            serializer = SubGroupSerializer(channel)
            return JsonResponse(serializer.data, status=200)

        except Group.DoesNotExist:
            return JsonResponse({'error': 'Channel not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    def delete(self, request, group_id):
        try:
            # Fetch the existing channel
            channel = Group.objects.filter(id=group_id).first()
            print(channel.name)
            channel.delete()
            return JsonResponse({'message': 'Channel deleted successfully'}, status=200)
        except Group.DoesNotExist:
            return JsonResponse({'error': 'Channel not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
