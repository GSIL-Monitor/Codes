package com.tsb.web.controller.org;

import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.tsb.admin.service.OrgService;
import com.tsb.model.org.Organization;
import com.tsb.util.RequestVO;
import com.tsb.web.controller.BaseController;

@Controller
@RequestMapping(value = "/api/admin/org")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class OrgCtrl extends BaseController {
	@Autowired
	private OrgService orgService;

	@RequestMapping(value = "/get", method = RequestMethod.POST)
	@ResponseBody
	public Map getOrg(@RequestBody RequestVO request) {
		String name = (String) request.getPayload().get("name");
		Map map = new HashMap();
		map.put("org", orgService.getOrg(name));
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/list", method = RequestMethod.POST)
	@ResponseBody
	public Map getOrgList(@RequestBody RequestVO request) {
		Map map = new HashMap();
		map.put("list", orgService.getOrgs());
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/add", method = RequestMethod.POST)
	@ResponseBody
	public Map addOrg(@RequestBody RequestVO request) throws Exception {
		ObjectMapper mapper = new ObjectMapper();
		String orgStr = mapper.writeValueAsString(request.getPayload().get("org"));
		Organization org = mapper.readValue(orgStr, Organization.class);
		orgService.addOrg(org);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/delete", method = RequestMethod.POST)
	@ResponseBody
	public Map deleteOrg(@RequestBody RequestVO request) {
		Integer id = (Integer) request.getPayload().get("id");
		orgService.deleteOrg(id);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/update", method = RequestMethod.POST)
	@ResponseBody
	public Map updateOrg(@RequestBody RequestVO request) throws Exception {
		ObjectMapper mapper = new ObjectMapper();
		String orgStr = mapper.writeValueAsString(request.getPayload().get("org"));
		Organization org = mapper.readValue(orgStr, Organization.class);
		orgService.update(org);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/countUser", method = RequestMethod.POST)
	@ResponseBody
	public Map countUser(@RequestBody RequestVO request) throws Exception {
		Integer id = (Integer) request.getPayload().get("id");
		Map map = orgService.coutOrgUsersInfo(id);
		map.put("code", 0);
		return map;
	}
	
//	@RequestMapping(value = "/usersInfo", method = RequestMethod.POST)
//	@ResponseBody
//	public Map orgOrgUsersInfo(@RequestBody RequestVO request) throws Exception {
//		Integer id = (Integer) request.getPayload().get("id");
//		Integer from = (Integer) request.getPayload().get("from");
//		Integer pageSize = (Integer) request.getPayload().get("pageSize");
//		
//		Map map= orgService.getOrgUsersInfo(id,from,pageSize);
//		map.put("code", 0);
//		return map;
//	}
	@RequestMapping(value = "/usersInfo", method = RequestMethod.POST)
	@ResponseBody
	public Map orgOrgUsersInfo(@RequestBody RequestVO request) throws Exception {
		Integer id = (Integer) request.getPayload().get("id");
		Map map= orgService.getOrgUsersInfo(id);
		map.put("code", 0);
		return map;
	}
}
