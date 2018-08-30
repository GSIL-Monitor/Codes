package com.tsb.company.service.async;

import java.util.Properties;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import com.tsb.vo.KafkaConstant;


@Service
public class KafkaAsync {
	@Autowired
	KafkaConstant kafkaConstant;
	
	@Async
	public void sendMsg(String msg){
		Properties props = new Properties();
		props.put("bootstrap.servers", kafkaConstant.getList());
		props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
		props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");
		props.put("acks", "1");
		Producer<String, String> producer = new KafkaProducer(props);
		producer.send(new ProducerRecord<String, String>("aggregator_v2", msg));
//		System.out.println(msg);
		producer.close();
	}
}
