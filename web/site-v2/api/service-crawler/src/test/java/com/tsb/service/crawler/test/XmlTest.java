package com.tsb.service.crawler.test;

import java.util.List;
import java.util.Map;

import org.junit.Test;
import org.springframework.beans.factory.annotation.Autowired;

import com.tsb.crawler.AlexaService;
import com.tsb.crawler.MemberService;

public class XmlTest extends BaseTest {
	@Autowired
	private MemberService memberService;
	@Autowired
	private AlexaService  alexaService;

	@SuppressWarnings("rawtypes")
	@Test
	public void xml() {
		
//		List list =(List) alexaService.findAlexa("http://www.mogujia.com", 100).get("alexaList");
		List list = memberService.getAll();
		if (list.size() > 0) {
			for (int i = 0; i < list.size(); i++) {
					System.out.println(list.get(i));
			}
		}
	}
//	@SuppressWarnings("rawtypes")
//	@Test
//	public void trends() {
//		List list = memberService.getTrends();
//		if (list.size() > 0) {
//			for (int i = 0; i < 10; i++) {
//					System.out.println(list.get(i));
//			}
//		}
//	}
//	@SuppressWarnings("rawtypes")
//	@Test
//	public void xml() {
//		Map map = alexaService.findAlexa("http://wangdian.cn", 30);
//		List  list = (List) map.get("alexaList");
//	}
	
}
