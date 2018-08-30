package com.tsb.web.controller.org;

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
import com.tsb.admin.service.UserService;
import com.tsb.model.user.User;
import com.tsb.util.RequestVO;
import com.tsb.web.controller.BaseController;

@Controller
@RequestMapping(value = "/api/admin/org/user")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class UserCtrl extends BaseController {
	@Autowired
	private UserService userService;

	@RequestMapping(value = "/get", method = RequestMethod.POST)
	@ResponseBody
	public Map getUser(@RequestBody RequestVO request) throws Exception {
		String email = (String) request.getPayload().get("email");
		Map map = new HashMap();
		map.put("exit",userService.getUser(email));
		map.put("code", 0);
		return map;
	}
	@RequestMapping(value = "/add", method = RequestMethod.POST)
	@ResponseBody
	public Map addUser(@RequestBody RequestVO request) throws Exception {
		
		ObjectMapper mapper = new ObjectMapper();
		String userStr = mapper.writeValueAsString(request.getPayload().get("user"));
		
		User user = mapper.readValue(userStr, User.class);
		Integer orgId = (Integer) request.getPayload().get("id");
		List<Integer> roles=  (List<Integer>) request.getPayload().get("roles");
		userService.addUser(orgId, user,roles);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/delete", method = RequestMethod.POST)
	@ResponseBody
	public Map deleteUser(@RequestBody RequestVO request) throws Exception {
		Integer id = (Integer) request.getPayload().get("id");
	
		Integer orgId = (Integer) request.getPayload().get("orgId");
		userService.deleteUser(id,orgId);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	@RequestMapping(value = "/update", method = RequestMethod.POST)
	@ResponseBody
	public Map updateUser(@RequestBody RequestVO request) throws Exception {	
		ObjectMapper mapper = new ObjectMapper();
		String userStr = mapper.writeValueAsString(request.getPayload().get("user"));
		User user = mapper.readValue(userStr, User.class);
		List roles=   (List) request.getPayload().get("roles");
		userService.update(user,roles);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}

}
