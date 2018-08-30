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

import com.fasterxml.jackson.databind.ObjectMapper;
import com.tsb.company.service.CompanyService;
import com.tsb.company.service.TagService;
import com.tsb.model.company.Footprint;
import com.tsb.model.company.Tag;
import com.tsb.util.RequestVO;

@Controller
@RequestMapping(value = "/api/company/tag")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class TagCtrl extends BaseController {
	@Autowired
	private TagService tagService;

	@RequestMapping(value = "/add", method = RequestMethod.POST)
	@ResponseBody
	public Map add(@RequestBody RequestVO request) {
		Integer userId = request.getUserid();
		List<Integer> ids = (List<Integer>) request.getPayload().get("ids");
		Integer companyId = (Integer) request.getPayload().get("companyId");

		tagService.addTagRels(companyId, ids, userId);

		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/delete", method = RequestMethod.POST)
	@ResponseBody
	public Map delete(@RequestBody RequestVO request) {
		Integer userId = request.getUserid();
		List ids = (List) request.getPayload().get("ids");
		Integer companyId = (Integer) request.getPayload().get("companyId");
		tagService.deleteTagRels(companyId, ids, userId);

		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/add/one", method = RequestMethod.POST)
	@ResponseBody
	public Map addTagRel(@RequestBody RequestVO request) throws Exception {
		Integer userId = request.getUserid();
		ObjectMapper mapper = new ObjectMapper();
		String add = mapper.writeValueAsString(request.getPayload().get("tag"));
		Tag tag = mapper.readValue(add, Tag.class);

		Integer companyId = (Integer) request.getPayload().get("companyId");

		tagService.addTagRel(companyId, tag, userId);

		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/delete/one", method = RequestMethod.POST)
	@ResponseBody
	public Map deleteTagRel(@RequestBody RequestVO request) {
		Integer userId = request.getUserid();
		Integer tagId = (Integer) request.getPayload().get("tagId");
		Integer companyId = (Integer) request.getPayload().get("companyId");
		tagService.deleteTagRel(companyId, tagId, userId);

		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/new", method = RequestMethod.POST)
	@ResponseBody
	public Map addNewTag(@RequestBody RequestVO request) {
		Integer userId = request.getUserid();
		String name = (String) request.getPayload().get("name");
		Tag tag = tagService.addTag(name, userId);
		Map map = new HashMap();
		map.put("code", 0);
		map.put("tag", tag);
		return map;
	}
	
	@RequestMapping(value = "/get", method = RequestMethod.POST)
	@ResponseBody
	public Map getByName(@RequestBody RequestVO request) {
		String name = (String) request.getPayload().get("name");
		Tag tag = tagService.getByName(name);
		Map map = new HashMap();
		map.put("code", 0);
		map.put("tag", tag);
		return map;
	}
}