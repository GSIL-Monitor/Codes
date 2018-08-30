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

import com.tsb.model.user.UserSetting;
import com.tsb.user.service.UserSectorService;
import com.tsb.user.service.UserSettingService;
import com.tsb.util.RequestVO;

@Controller
@RequestMapping(value = "/api/user/setting")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class SettingCtrl extends BaseController {

	@Autowired
	private UserSettingService userSettingService;
	
	@Autowired
	private UserSectorService userSectorService;

	@RequestMapping(value = "/get", method = { RequestMethod.POST })
	@ResponseBody
	public Map get(@RequestBody RequestVO request) {
		Integer userId = request.getUserid();
		
		UserSetting us = userSettingService.get(userId);
		List sectors = userSectorService.get(userId);
		
		Map map = new HashMap();
		map.put("code", 0);
		map.put("setting", us);
		map.put("sectors", sectors);
		return map;
	}
	
	@RequestMapping(value = "/update", method = { RequestMethod.POST })
	@ResponseBody
	public Map update(@RequestBody RequestVO request) {

		Integer userId = request.getUserid();
		int recommendNum = (int) request.getPayload().get("recommendNum");

		userSettingService.update(userId, recommendNum);

		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/updateAll", method = { RequestMethod.POST })
	@ResponseBody
	public Map updateAll(@RequestBody RequestVO request) {

		Integer userId = request.getUserid();
		int recommendNum = (int) request.getPayload().get("recommendNum");
		List newIds = (List) request.getPayload().get("newIds");
		List deleteIds = (List) request.getPayload().get("deleteIds");
		
		userSettingService.updateAll(userId, recommendNum, newIds, deleteIds);

		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	
	
}
