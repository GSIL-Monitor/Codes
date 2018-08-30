package com.tsb.web.controller.user;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.company.service.RecommendationService;
import com.tsb.util.RequestVO;
import com.tsb.web.controller.BaseController;


@Controller
@RequestMapping(value = "/api/company/recommend")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class RecommendationCtrl extends BaseController {
	@Autowired
	private RecommendationService rService;

	@RequestMapping(value = "/list", method = { RequestMethod.POST })
	@ResponseBody
	public Map getList(@RequestBody RequestVO request) {
		Integer userId = request.getUserid();
		List list = rService.get(userId);
		Map map = new HashMap();
		map.put("list", list);
		map.put("code", 0);
		return map;
	}
}
