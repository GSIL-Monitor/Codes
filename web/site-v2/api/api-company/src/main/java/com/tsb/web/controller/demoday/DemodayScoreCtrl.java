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
@RequestMapping(value = "/api/company/demoday/score")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class DemodayScoreCtrl extends BaseController{
	@Autowired
	private DemodayService demodayService;

	@RequestMapping(value = "/get", method = RequestMethod.POST)
	@ResponseBody
	public Map getScore(@RequestBody RequestVO request) {
		Integer userId = request.getUserid();
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		String code = (String) request.getPayload().get("code");
		Map result = demodayService.getScore(userId, demodayId, code);
		Map map = new HashMap();
		// demoday status
		map.put("status", result.get("scoringStatus"));
		map.put("score", result.get("demodayScore"));
		// orgId
		map.put("orgId", result.get("orgId"));
		map.put("partner", result.get("partner"));
		map.put("demodayUser", result.get("demodayUser"));
		map.put("code", 0);
		return map;

	}

	@RequestMapping(value = "/list", method = RequestMethod.POST)
	@ResponseBody
	public Map getCompanies(@RequestBody RequestVO request) {
		Integer userId = request.getUserid();
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		List demodayScoreVOList = demodayService.getScores(userId, demodayId);
		Map map = new HashMap();
		map.put("list", demodayScoreVOList);
		map.put("code", 0);
		return map;

	}

	@RequestMapping(value = "/score", method = RequestMethod.POST)
	@ResponseBody
	public Map demodayPrescore(@RequestBody RequestVO request) {
		Integer userId = request.getUserid();
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		String code = (String) request.getPayload().get("code");
		List<Integer> scores = (List<Integer>) request.getPayload().get("scores");

		demodayService.score(userId, demodayId, code, scores);
		Map map = new HashMap();
		map.put("code", 0);
		return map;

	}

}
