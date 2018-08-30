# -*- coding: utf-8 -*-
__author__ = 'victor'


import re


def get_name_template(key):

    return {
        "multi_match": {
            "query": key,
            "fields": ["name^3", "alias", "description"]
        }
    }


def get_string_template(column, key, min_percent="75%"):

    return {
        "query_string": {
            "default_field": column,
            "query": key,
            "minimum_should_match": min_percent
        }
    }


def get_tag_template(tag):

    return {
        "multi_match": {
            "query": tag,
            "type": "most_fields",
            "fields": ["description", "tags^5"]
        }}


def get_fast_tag_template(tag):

    return [
        {"term": {
            "tags": tag,
            "boost": 5
        }},
        # {"term": {
        #     "description": tag
        # }}
    ]


def get_restrict_tag_template(tag):

    return {
        "multi_match": {
            "query": tag,
            "type": "most_fields",
            "fields": ["tags^5"]
        }}


def get_keyword_template(*keywords):

    if len(keywords) == 1:
        return {
            "bool": {
                "should": [
                    {"term": {"tags": {"value": keywords[0], "boost": 2}}},
                    {"term": {"description": keywords[0]}},
                    {"term": {"name": {"value": keywords[0], "boost": 5}}}
                ]
            }
        }
    else:
        return {
            "bool": {
                "should": [
                    {"terms": {"tags": keywords}},
                    {"terms": {"description": keywords}},
                    {"term": {"name": {"value": ''.join(keywords), "boost": 5}}}
                ]
            }
        }


def get_industry_completion(key):

    return {
        "filtered": {
            "query": {
                "bool": {
                    "should": [
                        {"wildcard": {
                            "completionName": {
                                "value": "%s*" % key
                            }
                        }},
                        {"wildcard": {
                            "_name": {
                                "value": "*%s*" % key,
                                "boost": 10
                            }
                        }},
                        {"term": {
                            "_name": {
                                "value": key,
                                "boost": 20
                            }
                        }}
                    ],
                    "minimum_should_match": 1,
                    "must": [
                        {"terms": {
                            "active": ["Y"]
                        }}
                    ]
                }
            },
            "filter": {
                "term": {
                    "_prompt": "industry"
                }
            }
        }
    }


def get_field_completion(key, field, active=None):

    """
    completion of certain field
    :param key:
    :param field:
    :return:
    """
    if not active:
        return {
            "filtered": {
                "query": {
                    "bool": {
                        "should": [
                            {"wildcard": {
                                "completionName": {
                                    "value": "%s*" % key
                                }
                            }},
                            {"wildcard": {
                                "_name": {
                                    "value": "%s*" % key,
                                    "boost": 10
                                }
                            }},
                            {"term": {
                                "_name": {
                                    "value": key,
                                    "boost": 20
                                }
                            }}
                        ]
                    }
                },
                "filter": {
                    "term": {
                        "_prompt": field
                    }
                }
            }
        }
    else:
        return {
            "filtered": {
                "query": {
                    "bool": {
                        "should": [
                            {"wildcard": {
                                "completionName": {
                                    "value": "%s*" % key
                                }
                            }},
                            {"wildcard": {
                                "_name": {
                                    "value": "%s*" % key,
                                    "boost": 10
                                }
                            }},
                            {"term": {
                                "_name": {
                                    "value": key,
                                    "boost": 20
                                }
                            }}
                        ],
                        "minimum_should_match": 1,
                        "must": [
                            {"terms": {
                                "active": active
                            }}
                        ]
                    }
                },
                "filter": {
                    "term": {
                        "_prompt": field
                    }
                }
            }
        }


def get_investor_name_completion(key):

    return [
            {"wildcard": {
                "alias": {
                    "value": "%s*" % key
                }
            }},
            {"wildcard": {
                "name": {
                    "value": "%s*" % key,
                    "boost": 10
                }
            }},
            {"term": {
                "name": {
                    "value": key,
                    "boost": 20
                }
            }}
        ]


def get_investor_strict_completion(key):

    return {
        "bool": {
            "should": [
                {"wildcard": {
                    "_name": {
                        "value": "%s*" % key,
                        "boost": 10
                    }
                }},
                {"term": {
                    "_name": {
                        "value": key,
                        "boost": 20
                    }
                }}
            ],
            "minimum_should_match": 1,
            "must": [
                {"terms": {
                    "online": [True]
                }},
                {"term": {
                    "_prompt": "investor"
                }}
            ]
        }
    }


def get_investor_completion(key, tags=False, online=True):

    if not isinstance(online, list):
        online = [online]
    if tags:
        return {
            "bool": {
                "must": [
                    {"terms": {
                        "online": online
                    }},
                    {"term": {
                        "_prompt": "investor"
                    }},
                    {"terms": {
                        "features": key
                    }}
                ]
            }
        }
    else:
        return {
            "bool": {
                "should": [
                    {"wildcard": {
                        "completionName": {
                            "value": "%s*" % key
                        }
                    }},
                    {"wildcard": {
                        "_name": {
                            "value": "%s*" % key,
                            "boost": 10
                        }
                    }},
                    {"term": {
                        "_name": {
                            "value": key,
                            "boost": 20
                        }
                    }},
                    {"term": {
                        "features": key
                    }}
                ],
                "minimum_should_match": 1,
                "must": [
                    {"terms": {
                        "online": online
                    }},
                    {"term": {
                        "_prompt": "investor"
                    }}
                ]
            }
        }


def get_org_completion(key, org):

    return {
        "filtered": {
            "query": {
                "wildcard": {
                    "completionName": {
                        "value": "*%s*" % key
                    }
                }
            },
            "filter": {
                "term": {
                    "oid": org
                }
            }
        }
    }


def get_completion(key):

    """
    completion query
    :param key:
    :return:
    """
    return {
        "bool": {
            "should": [
                {"wildcard": {
                    "completionName": {
                        "value": "%s*" % key
                    }
                }},
                {"wildcard": {
                    "_name": {
                        "value": "%s*" % key,
                        "boost": 10
                    }
                }},
                {"term": {
                    "_name": {
                        "value": key,
                        "boost": 20
                    }
                }}
            ]
        }
    }


def get_new_completion(key, actives):

    return {
        "filtered": {
            "query": {
                "bool": {
                    "should": [
                        {"wildcard": {
                            "i_alias": {
                                "value": "%s*" % key
                            }
                        }},
                        {"wildcard": {
                            "name": {
                                "value": "%s*" % key,
                                "boost": 10
                            }
                        }},
                        {"term": {
                            "name": {
                                "value": key,
                                "boost": 20
                            }
                        }}
                    ]
                }
            },
            "filter": {
                "terms": {
                    "active": actives
                }
            }
        }
    }


def get_universal_completion(key, field=None, online=True):

    if not isinstance(online, list):
        online = [online]
    if not field:
        return {
            "bool": {
                "should": [
                    {"wildcard": {
                        "completionName": {
                            "value": "%s*" % key
                        }
                    }},
                    {"wildcard": {
                        "_name": {
                            "value": "%s*" % key,
                            "boost": 10
                        }
                    }},
                    {"term": {
                        "_name": {
                            "value": key,
                            "boost": 20
                        }
                    }}
                ],
                "must": [
                    {"terms": {
                        "online": online
                    }}
                ]
            }
        }
    else:
        return {
            "bool": {
                "should": [
                    {"wildcard": {
                        "completionName": {
                            "value": "%s*" % key
                        }
                    }},
                    {"wildcard": {
                        "_name": {
                            "value": "%s*" % key,
                            "boost": 10
                        }
                    }},
                    {"term": {
                        "_name": {
                            "value": key,
                            "boost": 20
                        }
                    }}
                ],
                "must": [
                    {"terms": {
                        "online": online
                    }},
                    {"term": {
                        "_prompt": field
                    }}
                ]
            }
        }


def get_amac_distinct_completion(key, distinct_field):

    return {
        "aggs": {
            "distinctId": {
                "filter": {
                    "query": {
                        "bool": {
                            "should": [
                                {"wildcard": {
                                    "amac_alias": {
                                        "value": "*%s*" % key
                                    }
                                }},
                                {"term": {
                                    "fundCode": key
                                }},
                                {"term": {
                                    "regCode": key
                                }}
                            ]
                        }
                    }
                },
                "aggs": {
                    "data": {
                        "terms": {
                            "field": distinct_field,
                            "size": 100
                        }
                    },
                    "count": {
                        "cardinality": {
                            "field": distinct_field
                        }
                    }
                }
            }
        }
    }


def get_amac_completion(key):

    return {
        "bool": {
            "should": [
                {"wildcard": {
                    "amac_alias": {
                        "value": "*%s*" % key
                    }
                }},
                {"term": {
                    "fundCode": key
                }},
                {"term": {
                    "regCode": key
                }}
            ]
        }
    }


def get_coin_completion(key, actives):

    return {
        "filtered": {
            "query": {
                "bool": {
                    "should": [
                        {"wildcard": {
                            "dt_alias": {
                                "value": "%s*" % key
                            }
                        }},
                        {"wildcard": {
                            "name": {
                                "value": "%s*" % key,
                                "boost": 10
                            }
                        }},
                        {"term": {
                            "symbol": {
                                "value": key,
                                "boost": 20
                            }
                        }}
                    ]
                }
            },
            "filter": {
                "terms": {
                    "active": actives
                }
            }
        }
    }


def get_fuzzy(column, key, boost=1):

    return {
        "wildcard": {
            "%s" % column: {
                "value": "*%s*" % key,
                "boost": boost
            }
        }
    }


def get_term(column, key, boost=1):

    return {
        "term": {
            "%s" % column: {
                "value": key,
                "boost": boost
            }
        }
    }


def get_round(keys):

    if 1060 in keys:
        keys = list(keys)
        keys.extend([1070, 1080, 1090, 1100, 1105, 1106, 1110, 1120, 1130, 1140])
    return {"terms": {
        "round": keys
    }}


def get_terms(column, keys):

    return {
        "terms": {
            "%s" % column: keys
        }
    }


def get_nested_template(path, column, keys):

    return {
        'nested': {
            'path': path,
            'query': {
                'terms': {'%s' % column: keys}
            }
        }
    }


def get_nested_term(column, category, keys):

    return {
        'nested': {
            'path': 'nested_tag',
            'query': {
                'bool': {
                    'must': [
                        {'term': {'nested_tag.category': category}},
                        {'term': {'%s' % column: keys}}
                    ]
                }
            }
        }
    }


def get_range(column, upper, lower):

    return {
        "range": {
            "%s" % column: {
                "gte": lower,
                "lte": upper
            }
        }
    }


def generate_rule_based_query(rule):

        if not rule:
            return {}

        criterias = {
            u'+': 'must',
            u'-': 'must_not',
            u',': 'should'
        }
        query = {}
        mix = re.findall('\((.*?)\)', rule)
        if len(mix) > 0:
            for subrule in mix:
                index = rule.index(subrule)
                if index > 1:
                    criteria = criterias[rule[index-2]]
                    query.setdefault('bool', {}).setdefault(criteria, []).append(generate_rule_based_query(subrule))
                else:
                    criteria = criterias[rule[index+len(subrule)+1]]
                    query.setdefault('bool', {}).setdefault(criteria, []).append(generate_rule_based_query(subrule))
        rule = re.sub('^\((.*?)\)[,\+\-]', '', rule)
        rule = re.sub('[,\+\-]\((.*?)\)', '', rule)
        rule = re.sub('\((.*?)\)', '', rule)
        # print rule, len(rule)
        if rule.strip() and not re.findall('[\+,\-]', rule):
            query.setdefault('bool', {}).setdefault('must', []).append(get_tag_template(rule))
            return query
        top = re.findall(u'(^[^\+,\-].*?[\+,\-])', rule)
        if top:
            criteria = criterias[top[0][-1]]
            query.setdefault('bool', {}).setdefault(criteria, []).append(get_tag_template(top[0][:-1]))
        # else:
        #     query.setdefault('bool', {}).setdefault('must', []).append(get_tag_template(rule))
        for not_term in re.findall(u'-([^\+,\-]*)', rule):
            query.setdefault('bool', {}).setdefault('must_not', []).append(get_tag_template(not_term))
        for and_term in re.findall(u'\+([^\+,\-]*)', rule):
            query.setdefault('bool', {}).setdefault('must', []).append(get_tag_template(and_term))
        for or_term in re.findall(u',([^\+,\-]*)', rule):
            query.setdefault('bool', {}).setdefault('should', []).append(get_tag_template(or_term))
            query.setdefault('bool', {}).setdefault('minimum_number_should_match', 1)

        return query


if __name__ == '__main__':

    print generate_rule_based_query(u'汽车+(数据,大数据)')