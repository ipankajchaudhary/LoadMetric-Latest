const dictt =
    {
        {
    "visualType": "card",
        "projections":
    {
        "Values":
        [
            {
                "queryRef": "Base.StoreDateInfo"
            }
        ]
    },
    "prototypeQuery":
    {
        "Version": 2,
            "From":
        [
            {
                "Name": "b",
                "Entity": "Base",
                "Type": 0
            }
        ],
            "Select":
        [
            {
                "Measure":
                {
                    "Expression":
                    {
                        "SourceRef":
                            { "Source": "b" }
                    }, "Property": "StoreDateInfo"
                }, "Name": "Base.StoreDateInfo"
            }]
    }, 
    "drillFilterOtherVisuals": True, 
    "hasDefaultSort": True, 
    "objects" : 
    { 
        "categoryLabels": 
        [
            { 
                "properties": 
                { 
                    "show": 
                    { "expr": { "Literal": { "Value": "false" } } } } }], "labels": [{ "properties": { "color": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 0, "Percent": 0 } } } } }, "fontSize": { "expr": { "Literal": { "Value": "9D" } } }, "fontFamily": { "expr": { "Literal": { "Value": """"Segoe UI"", wf_segoe- ui_normal, helvetica, arial, sans- serif""} } }, "preserveWhitespace": { "expr": { "Literal": { "Value": "false" } } } }
}] }, "vcObjects": { "background": [{ "properties": { "show": { "expr": { "Literal": { "Value": "false" } } }, "transparency": { "expr": { "Literal": { "Value": "0D" } } } } }], "title": [{ "properties": { "titleWrap": { "expr": { "Literal": { "Value": "true" } } } } }], "visualHeader": [{ "properties": { "show": { "expr": { "Literal": { "Value": "false" } } } } }], "dropShadow": [{ "properties": { "show": { "expr": { "Literal": { "Value": "false" } } }, "preset": { "expr": { "Literal": { "Value": ""Custom""} } }, "color": { "solid": { "color": { "expr": { "Literal": { "Value": ""#CCCACA"" } } } } }, "shadowDistance": { "expr": { "Literal": { "Value": "6D" } } } } }] } }}