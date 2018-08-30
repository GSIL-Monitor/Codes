package com.tsb.crawler.impl;

import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.stereotype.Service;

import com.mongodb.BasicDBObject;
import com.mongodb.DBCollection;
import com.mongodb.DBCursor;
import com.mongodb.DBObject;
import com.mongodb.util.JSON;
import com.tsb.crawler.MemberService;
import com.tsb.crawler.model.Alexa;

@Service
@SuppressWarnings({ "rawtypes", "unchecked" })
public class MemberServiceImpl implements MemberService {
	@Autowired
	private MongoTemplate mongoTemplate;

	@Override
	public List getAll() {
		List list = new ArrayList();
		// DBCollection memberCollection =
		// mongoTemplate.getCollection("member");
		DBCollection memberCollection = mongoTemplate.getCollection("trends_alexa");
		// 条件查询的对象,根据内嵌文档查询
		// BasicDBObject searchQuery = new
		// BasicDBObject("content.position","CTO");
		// DBCursor cursor = memberCollection.find(searchQuery).limit(10);
		BasicDBObject orderBy = new BasicDBObject("global_rank", -1);
		DBCursor cursor = memberCollection.find().sort(orderBy).limit(40);
		while (cursor.hasNext()) {
			DBObject object = cursor.next();
			list.add(JSON.parse(object.toString()));
		}
		System.out.println(list.size());
		return list;
	}

	public List getTrends() {
		return mongoTemplate.findAll(Alexa.class, "trends_alexa");

	}
}
