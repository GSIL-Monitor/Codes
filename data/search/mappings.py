# -*- coding: utf-8 -*-
__author__ = 'victor'


def get_company_mapping():

    """
    mapping of company, document of company, xiniudata
    :return:
    """
    return {
        "company": {
            "properties":
                {
                    "cid": {
                        "type": "string",
                        "index": "no"
                    },
                    "name": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "alias": {
                        "type": "string",
                        "analyzer": "whitespace"
                    },
                    "description": {
                        "type": "string",
                        "analyzer": "whitespace"
                    },
                    "tags": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "yellows": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "location": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "investors": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "members": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "team": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "investor": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "sector_l1": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "sector_l2": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "round": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "established": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "created": {
                        "type": "date"
                    },
                    "fa_date": {
                        "type": "date"
                    },
                    "num_cm": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "ranking_score": {
                        "type": "float",
                        "index": "not_analyzed"
                    }
                }
        }
    }


def get_completion_mapping():

    """
    the mapping of query input box completion text
    _name is the normal form of a term
    contents to be completed include:
    1. company name
    2. artifact name
    3. product name
    (1/2/3).1 alias
    4. tag
    5. location
    6. investor
    7. member

    id formats of completions includes:
    cxxxx, fxxx, axxxx, pxxxx, nxxxx, standing for company, full, artifact, product, nick
    kxxxx, keyword
    mxxxx, member
    ixxxx, investor
    lxxxx, location
    :return:
    """
    return {
        "completion": {
            "properties": {
                "_name": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "en_name": {
                    "type": "string"
                },
                "_code": {
                    "type": "string",
                    "index": "no"
                },
                "_prompt": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "id": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "completionName": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "ranking_score": {
                    "type": "float",
                    "index": "not_analyzed"
                },
                "online": {
                    "type": "boolean",
                    "index": "not_analyzed"
                },
                "active": {
                    "type": "string",
                    "index": "not_analyzed"
                }
            }
        }
    }
# "features": {
#                 "type": "string",
#                 "index": "not_analyzed"
#             },
# "feature_scores": {
#     "type": "string",
#     "index": "not_analyzed"
# }


def get_company_interior_mapping():

    return {
        "interior": {
            "properties": {
                "name": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "code": {
                    "type": "string",
                    "index": "no"
                },
                "id": {
                    "type": "string",
                    "index": "no"
                },
                "i_alias": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                'active': {
                    "type": "string",
                    "index": "not_analyzed"
                }
            }
        }
    }


def get_digital_token_mapping():

    return {
        "digital_token": {
            "properties": {
                "id": {
                    "type": "string",
                    "index": "no"
                },
                "name": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "symbol": {
                    "type": "string",
                    "index": "no"
                },
                "dt_alias": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                'active': {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "price": {
                    "type": "float",
                    "index": "not_analyzed"
                },
                "increase24h": {
                    "type": "float",
                    "index": "not_analyzed"
                },
                "turnover24h": {
                    "type": "long",
                    "index": "not_analyzed"
                },
                "circulationMarketValue": {
                    "type": "long",
                    "index": "not_analyzed"
                },
                "circulationQuantity": {
                    "type": "long",
                    "index": "not_analyzed"
                },
                "flowRate": {
                    "type": "float",
                    "index": "not_analyzed"
                },
                "totalCirculation": {
                    "type": "long",
                    "index": "not_analyzed"
                }
            }
        }
    }


def get_deal_mapping():

    return {
        "deal": {
            "properties":
                {
                    "did": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "oid": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "name": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "alias": {
                        "type": "string",
                        "analyzer": "whitespace"
                    },
                    "description": {
                        "type": "string",
                        "analyzer": "whitespace"
                    },
                    "tags": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "location": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "status": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "assignee": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "portfolioStatus": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "stage": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "portfolioStage": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "round": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "investment": {
                        "type": "long",
                        "index": "not_analyzed"
                    },
                    "postMoney": {
                        "type": "long",
                        "index": "not_analyzed"
                    },
                    "lastNoteTime": {
                        "type": "date"
                    }
                }
        }
    }


def get_deal_completion_mapping():

    return {
        "dealCompletion": {
            "properties": {
                "id": {
                    "type": "string",
                    "index": "no"
                },
                "did": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "oid": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "_name": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "completionName": {
                    "type": "string",
                    "index": "not_analyzed"
                }
            }
        }
    }


def get_news_mapping():

    return {
        "news": {
            "properties": {
                "id": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "title": {
                    "type": "string",
                    "analyzer": "whitespace"
                },
                "domain": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "link": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "content": {
                    "type": "string",
                    "analyzer": "whitespace"
                },
                "tags": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "features": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "type": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "category": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "status": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "date": {
                    "type": "integer",
                    "index": "not_analyzed"
                }
            }
        }
    }


def get_report_mapping():

    return {
        "report": {
            "properties": {
                "id": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "title": {
                    "type": "string",
                    "analyzer": "whitespace"
                },
                "domain": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "filename": {
                    "type": "string",
                    "analyzer": "whitespace"
                },
                "fileId": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "description": {
                    "type": "string",
                    "analyzer": "whitespace"
                },
                "md5": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "filesize": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "pages": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "date": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "createTime": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "modifyTime": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "reportType": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "marketSource": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "marketSymbol": {
                    "type": "string",
                    "index": "not_analyzed"
                }


            }
        }
    }


def get_universal_company_mapping():

    """
    mapping of company, new definition for universal search api
    """
    return {
        "universal": {
            "properties":
                {
                    "id": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "name": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "alias": {
                        "type": "string",
                        "analyzer": "whitespace"
                    },
                    "description": {
                        "type": "string",
                        "analyzer": "whitespace"
                    },
                    "nested_tag": {
                        "type": "nested",
                        "properties": {
                            "id": {"type": "integer", "index": "not_analyzed"},
                            "published": {"type": "date"},
                            "category": {"type": "string", "index": "not_analyzed"}
                        }
                    },
                    "tags": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "features": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "location": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "investors": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "investorId": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "members": {
                        "type": "string",
                        "index": "not_analyzed"
                    },
                    "sector": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "round": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "sort_round": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "status": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "established": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "created": {
                        "type": "date"
                    },
                    "last_funding_date": {
                        "type": "date"
                    },
                    "last_funding_amount": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "fa_date": {
                        "type": "date"
                    },
                    "num_cm": {
                        "type": "integer",
                        "index": "not_analyzed"
                    },
                    "ranking_score": {
                        "type": "float",
                        "index": "not_analyzed"
                    },
                    "sort_location": {
                        "type": "integer"
                    },
                    "sort_sector": {
                        "type": "integer"
                    }
                }
        }
    }


def get_universal_event_mapping():

    return {
        "event": {
            "properties": {
                "fid": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "investor": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "investorId": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "previous_investor": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "location": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "tags": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "sector": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "round": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "sort_round": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "last_funding_date": {
                    "type": "date"
                },
                "last_funding_amount": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "funding_year": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "funding_date": {
                    "type": "date"
                },
                "publish_date": {
                    "type": "date"
                },
                "source": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "sort_location": {
                    "type": "integer"
                },
                "sort_sector": {
                    "type": "integer"
                }
            }
        }
    }


def get_universal_investor_mapping():

    return {
        "investor": {
            "properties": {
                "iid": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "name": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "alias": {
                    "type": "string",
                    "analyzer": "whitespace"
                },
                "candidate": {
                    "type": "string",
                    "analyzer": "whitespace"
                },
                "location": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "online": {
                    "type": "boolean",
                    "index": "not_analyzed"
                },
                "active": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "investor_tag": {
                    "type": "nested",
                    "properties": {
                        "tag": {"type": "string", "index": "not_analyzed"},
                        "confidence": {"type": "float", "index": "not_analyzed"}
                    }
                },
                "round": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "portfolio_number": {
                    "type": "integer",
                    "index": "not_analyzed"
                },
                "portfolio_number_annual": {
                    "type": "integer",
                    "index": "not_analyzed"
                }
            }
        }
    }


def get_amac_mapping():

    # amac fund, basic element
    return {
        "amac": {
            "properties": {
                'amacid': {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "name": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "amac_alias": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "manager": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "managerId": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "fundCode": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "regCode": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "gp": {
                    "type": "integer",
                    "index": "not_analyzed"
                }
            }
        }
    }
