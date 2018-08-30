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

import com.tsb.company.service.DemodayService;
import com.tsb.util.RequestVO;
import com.tsb.web.controller.BaseController;

@Controller
@RequestMapping(value = "/api/company/demoday/org")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class DemodayOrgCtrl extends BaseController {
	@Autowired
	private DemodayService demodayService;

	@RequestMapping(value = "/list", method = RequestMethod.POST)
	@ResponseBody
	public Map getOrgList(@RequestBody RequestVO request) {
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		Map orgNames = demodayService.getDemodayOrgs(demodayId);
		Map map = new HashMap();
		// 参加的orgNames
		map.put("join", orgNames.get("join"));
		// 所有不参加的orgNames
		map.put("notJoin", orgNames.get("notJoin"));
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/add", method = RequestMethod.POST)
	@ResponseBody
	public Map addDemodayOrgList(@RequestBody RequestVO request) {
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		List<String> orgNames = (List<String>) request.getPayload().get("orgNames");
		// 参加
		Integer status = 28030;
		demodayService.updateDemodayOrgList(demodayId, status, orgNames);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/remove", method = RequestMethod.POST)
	@ResponseBody
	public Map removeDemodayOrgList(@RequestBody RequestVO request) {
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		List<String> orgNames = (List<String>) request.getPayload().get("orgNames");
		// 不参加
		Integer status = 28020;
		demodayService.updateDemodayOrgList(demodayId, status, orgNames);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
}
