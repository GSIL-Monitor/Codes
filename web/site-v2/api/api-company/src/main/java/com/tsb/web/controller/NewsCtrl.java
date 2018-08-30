package com.tsb.web.controller;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.company.service.NewsService;
import com.tsb.company.vo.NewsVO;
import com.tsb.util.RequestVO;

@Controller
@RequestMapping(value = "/api/company/news")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class NewsCtrl extends BaseController{

	@Autowired
	private NewsService newsService;
	
	@RequestMapping(value = "/list", method = RequestMethod.POST)
	@ResponseBody
	public Map getNewsList(@RequestBody RequestVO request) {
		int id = (int) request.getPayload().get("companyId");
		List newsList = newsService.get(id);
		Map map = new HashMap();
		map.put("list", newsList);
		map.put("code", 0);
		return map;

	}
	
	@RequestMapping(value = "/get", method = RequestMethod.POST)
	@ResponseBody
	public Map getNews(@RequestBody RequestVO request) {
		int companyId = (int) request.getPayload().get("companyId");
		int newsId = (int) request.getPayload().get("newsId");
		NewsVO newsVO = newsService.getVO(companyId, newsId);
		Map map = new HashMap();
		map.put("news", newsVO);
		map.put("code", 0);
		return map;

	}
}
