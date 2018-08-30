package com.tsb.service.crawler.test;

import org.bson.Document;
import org.junit.Test;

import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBCursor;
import com.mongodb.Mongo;
import com.mongodb.MongoClient;
import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;
import com.mongodb.util.JSON;

public class SimpleTest extends BaseTest {

	
	@SuppressWarnings("deprecation")
	@Test
	public void simpleTest() throws Exception{
		
		 try{   
		       // 连接到 mongodb 服务
		         MongoClient mongoClient = new MongoClient( "192.168.1.202" , 27017 );
		       
		         // 连接到数据库
		         MongoDatabase mongoDatabase = mongoClient.getDatabase("crawler_v2");  
		       System.out.println("Connect to database successfully");
		      
		       MongoCollection<Document> collection = mongoDatabase.getCollection("member");
		       FindIterable<Document> findIterable = collection.find();  
		         MongoCursor<Document> mongoCursor = findIterable.iterator();  
		         while(mongoCursor.hasNext()){  
		            System.out.println(mongoCursor.next());  
		         }  
		      }catch(Exception e){
		        System.err.println( e.getClass().getName() + ": " + e.getMessage() );
		     }
	}
}
