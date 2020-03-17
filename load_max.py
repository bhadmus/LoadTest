from locust import HttpLocust, TaskSet, task, between
import json

"""
When a proper load test is required, I created a 
file to where the user names and passwords could be read from
"""
# from usernames import details

details = [("username", "password")]
class UserBehavior(TaskSet):
    def __init__(self, parent):
        super(UserBehavior, self).__init__(parent)

        self.userName, self.password = details.pop()
        self.token = ""
        self.headers = {}

    def on_start(self):
        """
        This starts before anything else
        """
        self.data = self.login()
        self.token = self.data['access_token']
        self.uuid = self.data['user']['uuid']

    def login(self):
        """
        This will consume and return the login response
        so that the token and other things can be extracted
        :return: response body
        """
        resp = self.client.post("/auth-login", json={"username": self.userName, "password": self.password})
        resp_json = json.loads(resp._content)['data']
        return resp_json

    @task()
    def book_trip(self):
        self.client.post("/trip-requests", json={
            "origin": {
                "address": "25A Bisola Durosinmi Etti Dr, Lekki Phase 1, Lagos, Nigeria",
                "lat": 6.4372598,
                "lng": 3.4623144
            },
            "destination": {
                "address": "Sailor's Bar",
                "lat": 6.4412995,
                "lng": 3.4618351
            },
            "auto_dispatch": True,
            "is_cash": False,
            "user_id": self.uuid,
            "service_id": "<service_id_of_user>"
        }, headers={"Content-Type": "application/json", "authorization": f'Bearer {self.token}'})


class CustomerAppUser(HttpLocust):
    host = "https://base_url"
    task_set = UserBehavior
    wait_time = between(5, 15)
