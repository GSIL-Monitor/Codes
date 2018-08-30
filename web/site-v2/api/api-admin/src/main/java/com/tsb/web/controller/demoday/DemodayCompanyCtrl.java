package com.tsb.web.controller.demoday;

import java.util.ArrayList;
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
import com.tsb.admin.vo.DemodayCompanyVO;
import com.tsb.util.RequestVO;
import com.tsb.web.controller.BaseController;

@Controller
@RequestMapping(value = "/api/admin/demoday/company")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class DemodayCompanyCtrl extends BaseController {

	@Autowired
	private DemodayService demodayService;

	@RequestMapping(value = "/list", method = RequestMethod.POST)
	@ResponseBody
	public Map getDemodayCompanies(@RequestBody RequestVO request) {
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		
		List<DemodayCompanyVO> demodayCompanyVOList = demodayService.getDemodayCompanies(demodayId);
		Map map = new HashMap();
		map.put("list", demodayCompanyVOList);
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/update", method = RequestMethod.POST)
	@ResponseBody
	public Map updateDemodayCompany(@RequestBody RequestVO request) throws Exception {

		ObjectMapper mapper = new ObjectMapper();
		List<DemodayCompanyVO> demodayCompanyVOList = new ArrayList<DemodayCompanyVO>();
		List newCompanies = (List) request.getPayload().get("newCompanies");
		for (int i = 0, size = newCompanies.size(); i < size; i++) {
			String add = mapper.writeValueAsString(newCompanies.get(i));
			DemodayCompanyVO demodayCompanyVO = mapper.readValue(add, DemodayCompanyVO.class);
			demodayCompanyVOList.add(demodayCompanyVO);
		}
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		demodayService.updateDemodayCompanies(demodayId, demodayCompanyVOList);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	
	
	@RequestMapping(value = "/avgScores", method = RequestMethod.POST)
	@ResponseBody
	public Map getDemodayCompanyAvgScores(@RequestBody RequestVO request) {
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		Map map = new HashMap();
		map.put("list",demodayService.getCompanyAvgPreScore(demodayId));
		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/allScores", method = RequestMethod.POST)
	@ResponseBody
	public Map getDemodayCompanyPreScores(@RequestBody RequestVO request) {
		Integer dealDemodayId = (Integer) request.getPayload().get("dealDemodayId");
		Map map = new HashMap();
		map.put("list",demodayService.getAllUserPreScore(dealDemodayId));
		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/scoringStatus", method = RequestMethod.POST)
	@ResponseBody
	public Map scoringStatus(@RequestBody RequestVO request) {
		Integer id = (Integer) request.getPayload().get("demodayCompanyId");
		Integer scoringStatus = (Integer) request.getPayload().get("scoringStatus");
		demodayService.updateDemodayCompany(id, scoringStatus);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	@RequestMapping(value = "/batchStatus", method = RequestMethod.POST)
	@ResponseBody
	public Map batchStatus(@RequestBody RequestVO request) {
		List<Integer> ids =  (List<Integer>) request.getPayload().get("ids");
		Integer scoringStatus = (Integer) request.getPayload().get("scoringStatus");
		demodayService.updateDemodayCompany(ids, scoringStatus);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/batchJoinStatus", method = RequestMethod.POST)
	@ResponseBody
	public Map batchJoinStatus(@RequestBody RequestVO request) {
		List<Integer> ids =  (List<Integer>) request.getPayload().get("ids");
		Integer joinStatus = (Integer) request.getPayload().get("joinStatus");
		demodayService.updateDemodayCompanyJoinStatus(ids, joinStatus);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/remove", method = RequestMethod.POST)
	@ResponseBody
	public Map removeDemodayCompany(@RequestBody RequestVO request) {
		Integer id =   (Integer) request.getPayload().get("id");
		demodayService.removeDemodayCompany(id);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	
//	@RequestMapping(value = "/sysList", method = RequestMethod.POST)
//	@ResponseBody
//	public Map getSysListDemodayCompanies(@RequestBody RequestVO request) {
//		Integer demodayId = (Integer) request.getPayload().get("demodayId");
//		String orgName= (String) request.getPayload().get("orgName");
//		Integer start = (Integer) request.getPayload().get("start");
//		Integer pageSize = 20;
//		List<DemodayCompanyVO> demodayCompanyVOList = demodayService.getSysDemodayCompanies(demodayId,start,pageSize,orgName);
//		Map map = new HashMap();
//		map.put("list", demodayCompanyVOList);
//		map.put("code", 0);
//		return map;
//	}
	@RequestMapping(value = "/sysList", method = RequestMethod.POST)
	@ResponseBody
	public Map getSysListDemodayCompanies(@RequestBody RequestVO request) {
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		String orgName= (String) request.getPayload().get("orgName");
		List<DemodayCompanyVO> demodayCompanyVOList = demodayService.getSysDemodayCompanies(demodayId,orgName);
		Map map = new HashMap();
		map.put("list", demodayCompanyVOList);
		map.put("code", 0);
		return map;
	}
	@RequestMapping(value = "/pass", method = RequestMethod.POST)
	@ResponseBody
	public Map passSysListDemodayCompanies(@RequestBody RequestVO request) {
		List<Integer> demodayCompanyIds = (List<Integer>) request.getPayload().get("ids");
		 demodayService.updateSysDemodayCompanies(demodayCompanyIds,'Y');
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	@RequestMapping(value = "/notPass", method = RequestMethod.POST)
	@ResponseBody
	public Map notPassSysListDemodayCompanies(@RequestBody RequestVO request) {
		List<Integer> demodayCompanyIds = (List<Integer>) request.getPayload().get("ids");
		demodayService.updateSysDemodayCompanies(demodayCompanyIds,'N');
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
}
