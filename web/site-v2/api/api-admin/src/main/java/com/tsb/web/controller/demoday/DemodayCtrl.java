package com.tsb.web.controller.demoday;

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
import com.tsb.admin.service.DemodayService;
import com.tsb.model.demoday.Demoday;
import com.tsb.util.RequestVO;
import com.tsb.web.controller.BaseController;

@Controller
@RequestMapping(value = "/api/admin/demoday")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class DemodayCtrl  extends BaseController{
	@Autowired
	private DemodayService demodayService;

	@RequestMapping(value = "/get", method = RequestMethod.POST)
	@ResponseBody
	public Map getDemoday(@RequestBody RequestVO request) {
		String name = (String) request.getPayload().get("name");
		Map map = new HashMap();
		// check exist
		map.put("demoday", demodayService.getByName(name));
		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/detail", method = RequestMethod.POST)
	@ResponseBody
	public Map getDemodayById(@RequestBody RequestVO request) {
		Integer  demodayId= (Integer) request.getPayload().get("demodayId");
		Map map = new HashMap();
		// check exist
		map.put("demoday", demodayService.get(demodayId));
		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/orgList", method = RequestMethod.POST)
	@ResponseBody
	public Map getXOrgList(@RequestBody RequestVO request) {
		Integer status = (Integer) request.getPayload().get("status");
		Map map = new HashMap();
		// check exist
		map.put("list", demodayService.getXOrgList(status));
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/add", method = RequestMethod.POST)
	@ResponseBody
	public Map addDemoday(@RequestBody RequestVO request) throws Exception {
		List<Integer> orgIds = (List<Integer>) request.getPayload().get("orgIds");
		ObjectMapper mapper = new ObjectMapper();
		String demodayStr = mapper.writeValueAsString(request.getPayload().get("demoday"));
		Demoday demoday = mapper.readValue(demodayStr, Demoday.class);
		demodayService.addDemoday(demoday, orgIds);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/update", method = RequestMethod.POST)
	@ResponseBody
	public Map updateDemoday(@RequestBody RequestVO request) throws Exception {
		
		ObjectMapper mapper = new ObjectMapper();
		String demodayStr = mapper.writeValueAsString(request.getPayload().get("demoday"));
		Demoday demoday = mapper.readValue(demodayStr, Demoday.class);
		Map map = new HashMap();
		demodayService.updateDemoday(demoday);
		map.put("code", 0);
		return map;
	}

}
