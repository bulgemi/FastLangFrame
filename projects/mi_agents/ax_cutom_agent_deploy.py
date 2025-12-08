import logging

import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

IMAGE_TAG = "v0.0.1"
IMAGE_DESCRIPTION = "test version"

AIP_USER = "mip_sk_svc"
AIP_PASS = "Mip_sk_svc"
AIP_PROJECT = "MIP_SK"
AIP_BASE_URL = "https://aip.sktai.io"
MARI_AGENT_SERVING_ID = ""
IMAGE_URL = f"aip-harbor.sktai.io/sktai/custom/agent/mari_agent:{IMAGE_TAG}"


def login() -> str:
    response = requests.post(
        f"{AIP_BASE_URL}/api/v1/auth/login",
        headers={"Content-Type": "application/json"},
        json={"username": AIP_USER, "password": AIP_PASS, "project": AIP_PROJECT},
    )

    login_data = response.json()
    access_token = login_data.get("access_token")
    token_type = login_data.get("token_type")

    if not access_token:
        raise Exception(f"[ERROR] 로그인 실패 또는 토큰 획득 실패: {login_data}")

    auth_header = f"{token_type} {access_token}"
    logger.info(f"Authorization: {auth_header}")
    return auth_header


def is_first_deploy(auth_header: str) -> bool:
    return True


def update_agent(auth_header: str):
    agent_api_url = f"{AIP_BASE_URL}/api/v1/agent/agents/apps/custom"

    headers = {
        "Authorization": auth_header,
        "accept": "application/json",
    }

    response = requests.delete(agent_api_url, headers=headers)

    logger.info("에이전트 삭제 요청 완료")
    logger.info(f"Status Code: {response.status_code}")
    logger.info(f"Response: {response.text}")


def deploy_agent(auth_header: str):
    agent_api_url = f"{AIP_BASE_URL}/api/v1/agent/agents/apps/custom"

    headers = {
        "Authorization": auth_header,
        "accept": "application/json",
    }

    data = {
        "safety_filter_options": "{}",
        "cpu_limit": "1",
        "mem_request": "2",
        "target_type": "external_graph",
        "min_replicas": "1",
        "image_url": IMAGE_URL,
        "workers_per_core": "3",
        "name": "mari_agent",
        "registry_url": "",
        "serving_type": "standalone",
        "mem_limit": "2",
        "model_list": "skmidev-gpt-4-1-20250414",
        "version_description": IMAGE_DESCRIPTION,
        "image_tag": "",
        "max_replicas": "1",
        "cpu_request": "1",
        "use_external_registry": "false",
        "description": "MI Project",
    }

    with open(".env", "rb") as env_file:
        files = {"env_file": env_file}
        response = requests.post(agent_api_url, headers=headers, data=data, files=files)

    logger.info("배포 요청 완료")
    logger.info(f"Status Code: {response.status_code},\nResponse: {response.text}")


def main():
    try:
        auth_header = login()
        is_first = is_first_deploy(auth_header)
        logger.info(f"is_first: {is_first}")
        # if is_first:
        #   deploy_agent(auth_header)
        # else:
        #   update_agent(auth_header)

    except Exception as e:
        logger.error(f"배포 요청 실패: {e}")


if __name__ == "__main__":
    main()
