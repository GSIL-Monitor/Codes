package com.tsb.web.controller.demoday;

import java.util.HashMap;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.company.service.DemodayService;
import com.tsb.company.vo.DemodayResultVO;
import com.tsb.util.RequestVO;
import com.tsb.web.controller.BaseController;

@Controller
@RequestMapping(value = "/api/company/demoday/result")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class DemodayResultCtrl extends BaseController{

	@Autowired
	private DemodayService demodayService;

	@RequestMapping(value = "/list", method = RequestMethod.POST)
	@ResponseBody
	public Map getDemodayResult(@RequestBody RequestVO request) {

		Integer userId = request.getUserid();
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		String code = (String) request.getPayload().get("code");
		DemodayResultVO demodayResultVO = demodayService.getResult(userId, demodayId, code);
		Map map = new HashMap();
		map.put("code", 0);
		map.put("result", demodayResultVO);

		return map;
	}

	@RequestMapping(value = "/invest", method = RequestMethod.POST)
	@ResponseBody
	public Map invest(@RequestBody RequestVO request) {

		Integer userId = request.getUserid();
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		String code = (String) request.getPayload().get("code");
		// TODO
		Integer result = (Integer) request.getPayload().get("result");
		demodayService.invest(userId, demodayId, code, result);
		Map map = new HashMap();
		map.put("code", 0);

		return map;
	}
}
