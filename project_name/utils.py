import requests
import io
import boto3
import simplejson as json
from PIL import Image, ImageFilter
from django.conf import settings
from twilio.rest import TwilioRestClient
from twilio import TwilioRestException

import tinify
tinify.key = settings.TINYPNG


HEADER = {
    'Content-Type': 'application/json; charset=utf-8',
    'Authorization': 'Basic {}'.format(settings.ONE_SIGNAL_REST_KEY)
}


def notification_template(instance):

    # 'Loud' Push Notification
    push_message = """Push Notification Message. Customize."""

    payload = {
        "app_id": "{}".format(settings.ONE_SIGNAL_APP_ID),
        "included_segments": ["All"],
        "contents": {"en": push_message},
        "android_background_data": True,
        "data": {
            "action": "",
        }
    }

    req = requests.post(
        "https://onesignal.com/api/v1/notifications",
        headers=HEADER, data=json.dumps(payload)
    )

    print(req.status_code, req.reason)

    # Silent Push Notification
    payload = {
        "app_id": "{}".format(settings.ONE_SIGNAL_APP_ID),
        "included_segments": ["All"],
        "content_available": True,
        "android_background_data": True,
        "data": {
            "action": "",
        }
    }

    req = requests.post(
        "https://onesignal.com/api/v1/notifications",
        headers=HEADER, data=json.dumps(payload)
    )
    print(req.status_code, req.reason)


def upload_to_s3_from_data(data, path):

    client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

    client.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=path, Body=data.getvalue()
    )

    url = client.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': path
        }
    )
    print(url)


def compress_image(instance):

    if hasattr(instance, 'image'):

        if instance.image != '':

            filename = '.'.join(instance.image.split('.')[:-1])
            ext = instance.image.split('.')[-1]
            after_uploads = filename.split('uploads')[-1]
            file_path = '{}_compressed.{}'.format(after_uploads, ext)

            source = tinify.from_url(instance.image)
            source.store(
                service='s3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region=settings.S3DIRECT_REGION,
                path='{}/uploads{}'.format(settings.AWS_STORAGE_BUCKET_NAME, file_path)
            )


def make_thumbnail(instance, size):
    pass

    # send url to tinypng smart crop,
    # receive the image
    # send the image to S3
    # save the url to the instance


def make_placeholder_image(instance, b=42):

    if hasattr(instance, 'image'):
        if instance.image != '':
            image_data = requests.get(instance.image)
            data = io.BytesIO(image_data.content)
            im = Image.open(data)
            im = im.filter(ImageFilter.BLUR)

            r = (b / float(im.size[0]))
            h = int((float(im.size[1]) * float(r)))

            im = im.resize((b, h), Image.ANTIALIAS)

            filename = '.'.join(instance.image.split('.')[:-1])
            ext = instance.image.split('.')[-1]
            after_uploads = filename.split('uploads')[-1]
            file_path = 'uploads{}_placeholder.{}'.format(after_uploads, ext)

            output = io.BytesIO()
            if ext == 'jpg' or ext == 'jpeg':
                im.save(output, format='JPEG')
            elif ext == 'png':
                im.save(output, format='PNG')

            upload_to_s3_from_data(output, file_path)


# def send_sms(message, destination):
#
#     try:
#         # Send sms to user
#         client = TwilioRestClient(settings.TWILIO_ACCOUND_SID, settings.TWILIO_AUTH_TOKEN)
#         twilio_sms_message = client.messages.create(
#             to='{}'.format(destination), from_='{}'.format(settings.TWILIO_PHONE_NUMBER),
#             body=message
#         )
#
#         #return (response_code, "message was sent succesfully")
#
#     except TwilioRestException as e:
#
#         # Check Exception message for issues that is the user's fault
#         # return success callback
#
#         # Twilio failed try Plivo
#
#         client = plivo.RestAPI(settings.PLIVO_AUTH_ID, settings.PLIVO_AUTH_TOKEN)
#         params = {
#             'src': settings.PLIVO_PHONE_NUMBER,
#             'dst': u"{}".format(destination),
#             'text': u"{}".format(message),
#             'method': 'POST'
#         }
#
#         response = client.send_message(params)
#         response_code = int(response[0])
#
#         if response_code >= 400:
#             # Handle Errors
#             pass
#             # return (response_code, "error description")
#         else:
#             # Successfull
#             pass
#             # return (response_code, "message was sent successfully")


