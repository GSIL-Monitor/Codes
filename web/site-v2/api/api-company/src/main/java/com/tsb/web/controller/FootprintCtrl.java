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

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.tsb.company.service.FootprintService;
import com.tsb.company.vo.CompanyVO;
import com.tsb.model.company.Footprint;
import com.tsb.model.company.News;
import com.tsb.util.RequestVO;

@Controller
@RequestMapping(value = "/api/company/footprint")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class FootprintCtrl extends BaseController {
	@Autowired
	private FootprintService footprintService;

	@RequestMapping(value = "/list", method = RequestMethod.POST)
	@ResponseBody
	public Map getFootprints(@RequestBody RequestVO request) {
		int id = (int) request.getPayload().get("id");
		List list = footprintService.get(id);
		
		Map map = new HashMap();
		map.put("footprints", list);
		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/add", method = RequestMethod.POST)
	@ResponseBody
	public Map add(@RequestBody RequestVO request) throws Exception {
		List footprints = (List) request.getPayload().get("footprints");
		List newFootprints = new ArrayList();
		ObjectMapper mapper = new ObjectMapper();
		
		for(int i=0; i< footprints.size(); i++){
			String add = mapper.writeValueAsString(footprints.get(i));
			Footprint footprint = mapper.readValue(add, Footprint.class);
			newFootprints.add(footprint);
		}
		
		int userId = request.getUserid();
		
		footprintService.addFootprints(newFootprints, userId);
		
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/update", method = RequestMethod.POST)
	@ResponseBody
	public Map update(@RequestBody RequestVO request)  throws Exception {
		List footprints = (List) request.getPayload().get("footprints");
		List updateFootprints = new ArrayList();
		ObjectMapper mapper = new ObjectMapper();
		
		for(int i=0; i< footprints.size(); i++){
			String add = mapper.writeValueAsString(footprints.get(i));
			Footprint footprint = mapper.readValue(add, Footprint.class);
			updateFootprints.add(footprint);
		}
		
		int userId = request.getUserid();
		
		footprintService.updateFootprints(updateFootprints, userId);
		
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	
	
	@RequestMapping(value = "/delete", method = RequestMethod.POST)
	@ResponseBody
	public Map delete(@RequestBody RequestVO request) {
		List ids = (List) request.getPayload().get("ids");
		int userId = request.getUserid();
		footprintService.deleteFootprints(ids, userId);
		
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	
}