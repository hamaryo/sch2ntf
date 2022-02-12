import io
import json
import base64

import oci
from fdk import response

def handler(ctx, data: io.BytesIO = None):
    cfg = dict(ctx.Config())
    topic_id = cfg["TOPIC_ID"]

    # extract data from service connector hub
    entries = json.loads(data.getvalue())
    for entry in entries:
        key = base64.b64decode(bytes(entry["key"], "utf-8")).decode()
        value = base64.b64decode(bytes(entry["value"], "utf-8")).decode()
        publish_message(topic_id, "{}: {}".format(key, value))

    return response.Response(
        ctx, response_data=json.dumps(
            {"message": "Succeeded"}),
        headers={"Content-Type": "application/json"}
    )

def publish_message(topic_id: str, message: str):
    signer = oci.auth.signers.get_resource_principals_signer()
    ons_client = oci.ons.NotificationDataPlaneClient(config={}, signer=signer)
    message_detail = oci.ons.models.MessageDetails(body=message)
    ons_client.publish_message(topic_id, message_detail)
