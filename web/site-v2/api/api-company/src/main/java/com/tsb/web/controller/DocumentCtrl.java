package com.tsb.web.controller;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.tsb.company.service.DocumentService;
import com.tsb.model.company.Document;
import com.tsb.util.RequestVO;

@Controller
@RequestMapping(value = "/api/company/document")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class DocumentCtrl extends BaseController {
	@Autowired
	private DocumentService documentService;

	@RequestMapping(value = "/list", method = RequestMethod.POST)
	@ResponseBody
	public Map getFootprints(@RequestBody RequestVO request) {
		int id = (int) request.getPayload().get("id");
		List list = documentService.getAll(id);
		
		Map map = new HashMap();
		map.put("documents", list);
		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/add", method = RequestMethod.POST)
	@ResponseBody
	public Map add(@RequestBody RequestVO request) throws Exception {
		List documents = (List) request.getPayload().get("documents");
		List news = new ArrayList();
		ObjectMapper mapper = new ObjectMapper();
		
		for(int i=0; i< documents.size(); i++){
			String add = mapper.writeValueAsString(documents.get(i));
			Document document = mapper.readValue(add, Document.class);
			news.add(document);
		}
		
		int userId = request.getUserid();
		
		documentService.add(news, userId);
		
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	
	
	@RequestMapping(value = "/delete", method = RequestMethod.POST)
	@ResponseBody
	public Map delete(@RequestBody RequestVO request) {
		List ids = (List) request.getPayload().get("ids");
		int userId = request.getUserid();
		documentService.delete(ids, userId);
		
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	
}