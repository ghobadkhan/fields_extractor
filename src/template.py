

# Da Template
template = {
    "top-domain": [
        {
            "sub-domain": "*",
            "sign-in": {
                "etc": "*"
            },
            "next-page": None,
            "application": {
                "field-id": ...,
                
            }
        }
    ],
    "myworkday": {
        "url_regex": r"(.*)\.wd\d\.myworkdayjobs\.com",
        "items": [
            {
                "name": None,
                "url_name": None,
                "default": {
                    # xpath -  div elements that have the attribute 'data-automation-id' with value
                    # which starts with 'formField'
                    "form_field": "//div[contains(@data-automation-id,'formField')]"
                },
                "sign_in": {
                    "indicator": {},
        
                }
            }
        ]
    }
}