
JSON_data = """{
    "description": "asdasdasd",
    "name": "asdasd",
    "slug": "application_slug",
    "responses": [
        {
            "status_code": 201,
            "creator": null,
            "resources": [
                {
                    "description": "application_resource_description",
                    "method": "GET",
                    "proxy_destination_address": null,
                    "response_type": "CUSTOM",
                    "slug": "application_resource_slug",
                    "tail": "dadas",
                    "creator": null,
                    "is_enabled": true,
                    "inject_stubborn_headers": false,
                    "hooks": [
                        {
                            "action": "webhook",
                            "lifecycle": "before",
                            "order": 1,
                            "timeout": 0,
                            "request": {
                                "name": "hook_request_name",
                                "query_params": {
                                    "q1": "333",
                                    "ddd": "fff"
                                },
                                "uri": "http://127.0.0.1/ffff/adadad",
                                "method": "GET"
                            }
                        }
                    ]
                }
            ]
        }
    ]
}"""
