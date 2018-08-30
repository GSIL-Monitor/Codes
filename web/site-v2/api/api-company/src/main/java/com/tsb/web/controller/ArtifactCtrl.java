package com.tsb.web.controller;

import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.company.service.ArtifactService;
import com.tsb.company.service.TrendsService;
import com.tsb.util.RequestVO;

@Controller
@RequestMapping(value = "/api/company/artifact")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class ArtifactCtrl extends BaseController {
	@Autowired
	private ArtifactService artifactService;
	@Autowired
	private TrendsService trendsService;

	@RequestMapping(value = "/list", method = RequestMethod.POST)
	@ResponseBody
	public Map getArtifacts(@RequestBody RequestVO request) {
		int id = (int) request.getPayload().get("id");
		List<Integer> typeList = artifactService.getArtifactTypeList(id);
		Map map = artifactService.getArtifacts(id, 0, 20);
		map.put("types", typeList);
		map.put("code", 0);
		return map;
	}
	
	
	@RequestMapping(value = "/trends", method = RequestMethod.POST)
	@ResponseBody
	public Map getTrends(@RequestBody RequestVO request) {
		Integer  companyId = (Integer) request.getPayload().get("companyId");
		Integer artifactId = (Integer) request.getPayload().get("artifactId");
		Integer artifactType = (Integer) request.getPayload().get("artifactType");
		//拓展的天数
		Integer expand = (Integer) request.getPayload().get("expand");
		Map map= trendsService.getTrends(companyId, artifactId,artifactType,expand);
		map.put("code", 0);
		return map;
	}

}
