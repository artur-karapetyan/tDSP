import random

import requests

BASE_URL = "http://0.0.0.0:9090"
GAME_CONFIGURATION_URL = BASE_URL + "/game/configure/"
RTB_BID_REQUEST_URL = BASE_URL + "/rtb/bid/"
RTB_NOTIFY_URL = BASE_URL + "/rtb/notify/"
CREATIVES_URL = BASE_URL + "/api/creatives/"
CAMPAIGNS_URL = BASE_URL + "/api/campaigns/"

IMPRESSION_REVENUE = 2


def _get_configuration_body(**kwargs):
    data = {
        "impressions_total": 10,
        "auction_type": random.choice([1, 2]),
        "game_goal": "revenue",
        "mode": random.choice(["free", "script"]),
        "budget": 10,
        "impression_revenue": IMPRESSION_REVENUE,
        "click_revenue": 5,
        "conversion_revenue": 10,
        "frequency_capping": 100
    }

    data.update(kwargs)
    return data


def _send_bid_request_and_check_response(bid_request_data):
    response = requests.post(RTB_BID_REQUEST_URL, json=bid_request_data)
    assert response.status_code in (200, 204)
    if response.status_code == 204:
        return None

    response_data = response.json()
    for field in ["external_id", "price", "image_url", "cat"]:
        if field not in response_data:
            raise Exception("Bid Response does not contain field {}".format(field))

    return response_data


def _send_loss_and_check_response(request_id):
    response = requests.post(RTB_NOTIFY_URL, json={"id": request_id, "win": False})
    assert response.status_code == 200


def _send_win_and_check_response(request_id, bid_response_body):
    response = requests.post(RTB_NOTIFY_URL, json={
        "id": request_id,
        "win": True,
        "price": bid_response_body["price"],
        "click": False,
        "conversion": False,
        "revenue": IMPRESSION_REVENUE,
    })
    assert response.status_code == 200


def test_configuration():
    body = _get_configuration_body()
    response = requests.post(GAME_CONFIGURATION_URL, json=body)
    assert response.status_code == 200


def test_script_game():
    body = _get_configuration_body(impressions_total=3, mode="script")
    response = requests.post(GAME_CONFIGURATION_URL, json=body)
    assert response.status_code == 200

    response = requests.post(CAMPAIGNS_URL, json={"budget": body["budget"], "name": "test_campaign"})
    assert response.status_code == 201
    campaign_data = response.json()
    assert "id" in campaign_data
    assert campaign_data["name"] == "test_campaign"

    base64png = "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"
    external_id = "test_creative_id"
    categories = [{"code": "IAB1-1"}, {"code": "IAB2-2"}, {"code": "IAB3"}]
    response = requests.post(CREATIVES_URL, json={
        "external_id": external_id,
        "campaign": campaign_data,
        "categories": categories,
        "name": "test_creative",
        "file": base64png,
    })
    assert response.status_code == 201
    creative_data = response.json()
    assert creative_data["external_id"] == external_id
    assert creative_data["name"] == "test_creative"
    assert "id" in creative_data
    assert "url" in creative_data
    assert "categories" in creative_data
    assert {x["code"] for x in categories} == {x["code"] for x in creative_data["categories"]}

    bid_request_body = {
        "id": "id_1",
        "imp": {"banner": {"w": 25, "h": 25}},
        "bcat": [],
        "click": {"prob": 0.5}, "conv": {"prob": 0.89},
        "site": {"domain": "www.example.com"}, "ssp": {"id": "0938831"}, "user": {"id": "u_cq_001_87311"},
    }
    bid_response_body = _send_bid_request_and_check_response(bid_request_body)
    if bid_response_body:
        assert bid_response_body["external_id"] == external_id
        _send_loss_and_check_response("id_1")

    bid_request_body["id"] = "id_2"
    bid_response_body = _send_bid_request_and_check_response(bid_request_body)
    if bid_response_body:
        assert bid_response_body["external_id"] == external_id
        _send_win_and_check_response("id_2", bid_response_body)

    bid_request_body["id"] = "id_3"
    bid_response_body = _send_bid_request_and_check_response(bid_request_body)
    if bid_response_body:
        assert bid_response_body["external_id"] == external_id
        _send_win_and_check_response("id_3", bid_response_body)


if __name__ == "__main__":
    test_configuration()
    test_script_game()