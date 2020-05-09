import base64
import jsonpatch

from flask import Flask, request, jsonify


admission_controller = Flask(__name__)
container_path = "/spec/containers"
side_car_config = {"name": "busybox2",
                   "image": "busybox",
                   "command": ["sleep", "3600"],
                   "imagePullPolicy": "IfNotPresent"}


@admission_controller.route('/mutate/pods', methods=['POST'])
def add_side_car_webhook():
    request_info = request.get_json()
    containers = request_info['request']['object']['spec']['containers']
    containers.append(side_car_config)
    return admission_response_patch(True,
                                    request_info['request']['uid'],
                                    "Adding side car",
                                    json_patch=jsonpatch.JsonPatch([{"op": "add",
                                                                     "path": container_path,
                                                                     "value": containers}]))


def admission_response_patch(allowed, uid, message, json_patch):
    base64_patch = base64.b64encode(json_patch.to_string().encode("utf-8")).decode("utf-8")
    return jsonify({"apiVersion": "admission.k8s.io/v1",
                    "kind": "AdmissionReview",
                    "response": {"allowed": allowed,
                                 "status": {"message": message},
                                 "uid": uid,
                                 "patchType": "JSONPatch",
                                 "patch": base64_patch}})

if __name__ == '__main__':
    admission_controller.run(host='0.0.0.0', port=443, ssl_context=("/certs/cert.pem", "/certs/key.pem"))
