JSON_data = """
{
  "description": "asdasdasd",
  "name": "asdasd",
  "slug": "application_slug",
  "resources": [
    {
      "description": "resources_description",
      "method": "GET",
      "proxy_destination_address": null,
      "response_type": "CUSTOM",
      "slug": "aawddddd",
      "tail": "dadas",
      "is_enabled": true,
      "inject_stubborn_headers": false,
      "response": {
        "status_code": 200
      },
      "hooks": [
        {
          "action": "webhook",
          "lifecycle": "before",
          "order": 1,
          "timeout": 0,
          "request": {
            "name": "awdawddddd",
            "query_params": { "q1": "333", "ddd": "fff" },
            "uri": "http://127.0.0.1/ffff/adadad",
            "method": "GET"
          }
        }
      ]
    }
  ],
  "responses": [
    {
        "status_code": 400
    },
    {
        "status_code": 500
    }
  ],
  "requests": [
    {
        "name": "awdawddddd1",
        "query_params": { "q": "sss"},
        "uri": "http://127.0.0.1/ffff/adadad1",
        "method": "GET"
    },
    {
        "name": "awdawddddd2",
        "query_params": { "cc": "vv" },
        "uri": "http://127.0.0.1/ffff/adadad2",
        "method": "GET"
    }
  ]
}
"""
