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
import com.tsb.company.vo.DemodayPreScoreVO;
import com.tsb.util.RequestVO;
import com.tsb.web.controller.BaseController;

@Controller
@RequestMapping(value = "/api/company/demoday/preScore")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class DemodayPreScoreCtrl extends BaseController {
	@Autowired
	private DemodayService demodayService;

	@RequestMapping(value = "/get", method = RequestMethod.POST)
	@ResponseBody
	public Map getPreScore(@RequestBody RequestVO request) {
		Integer userId = request.getUserid();
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		String code = (String) request.getPayload().get("code");
		Map result = demodayService.getPrescore(userId, demodayId, code);
		Map map = new HashMap();
		// demoday status
		map.put("status", result.get("scoringStatus"));
		map.put("preScore", result.get("preScore"));
		map.put("demodayUser", result.get("demodayUser"));
		map.put("last", result.get("last"));
		map.put("nextCode",  result.get("nextCode"));
		map.put("code", 0);
		return map;

	}

	@RequestMapping(value = "/list", method = RequestMethod.POST)
	@ResponseBody
	public Map getCompanies(@RequestBody RequestVO request) {
		Integer userId = request.getUserid();
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		List<DemodayPreScoreVO> demodayCompanyVOList = demodayService.getPreScores(userId, demodayId);
		Map map = new HashMap();
		map.put("list", demodayCompanyVOList);
		map.put("code", 0);
		return map;

	}

	@RequestMapping(value = "/score", method = RequestMethod.POST)
	@ResponseBody
	public Map demodayPrescore(@RequestBody RequestVO request) {
		Integer userId = request.getUserid();
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		String code = (String) request.getPayload().get("code");
		int score = (int) request.getPayload().get("score");
		demodayService.preScore(userId, demodayId, code, score);
		Map map = new HashMap();
		map.put("code", 0);
		return map;

	}

}
