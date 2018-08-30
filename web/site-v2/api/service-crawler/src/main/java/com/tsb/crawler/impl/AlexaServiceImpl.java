package com.tsb.crawler.impl;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;

import com.mongodb.BasicDBObject;
import com.mongodb.DBCollection;
import com.mongodb.DBCursor;
import com.mongodb.DBObject;
import com.mongodb.util.JSON;
import com.tsb.crawler.AlexaService;
@SuppressWarnings({ "rawtypes", "unchecked" })
public class AlexaServiceImpl implements AlexaService {
	@Autowired
	private MongoTemplate mongoTemplate;

	protected DBCollection getCollection() {
		return mongoTemplate.getCollection("trends_alexa");
	}

	
	@Override
	public Map findAlexa(String domain, int limit) {
		List list = new ArrayList();
		DBCollection alexaCollection =getCollection(); 
		BasicDBObject query  = new BasicDBObject("domain",domain); 
		BasicDBObject orderBy = new BasicDBObject("date",-1);
		 DBCursor cursor = alexaCollection.find(query).sort(orderBy).limit(limit);
		 while (cursor.hasNext()) {
				DBObject object = cursor.next();
				list.add(JSON.parse(object.toString()));
			}
		 Map map = new HashMap();
		 map.put("alexaList", list);
		 return map;
	}

}
