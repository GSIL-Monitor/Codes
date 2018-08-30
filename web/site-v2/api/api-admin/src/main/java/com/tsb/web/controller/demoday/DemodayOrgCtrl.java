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

import com.tsb.admin.service.DemodayService;
import com.tsb.admin.vo.DemodayOrgVO;
import com.tsb.util.RequestVO;
import com.tsb.web.controller.BaseController;

@Controller
@RequestMapping(value = "/api/admin/demoday/org")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class DemodayOrgCtrl extends BaseController{
	@Autowired
	private DemodayService demodayService;
	
	@RequestMapping(value = "/list", method = RequestMethod.POST)
	@ResponseBody
	public Map getDemodayOrgs(@RequestBody RequestVO request) {
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		
		List<DemodayOrgVO> demodayOrgVOList = demodayService.getDemodayOrgs(demodayId);
		Map map = new HashMap();
		map.put("list", demodayOrgVOList);
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/reject", method = RequestMethod.POST)
	@ResponseBody
	public Map rejectDemodayOrg(@RequestBody RequestVO request) {

		Integer orgId = (Integer) request.getPayload().get("orgId");
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		Map map = new HashMap();
		demodayService.updateDemodayOrg(demodayId, orgId, 28020);
		map.put("code", 0);
		return map;
	}

	@RequestMapping(value = "/join", method = RequestMethod.POST)
	@ResponseBody
	public Map joinDemodayOrg(@RequestBody RequestVO request) {

		List<Integer> orgIds = (List<Integer>) request.getPayload().get("orgIds");
		Integer demodayId = (Integer) request.getPayload().get("demodayId");
		Map map = new HashMap();
		demodayService.updateDemodayOrg(demodayId, orgIds, 28030);
		map.put("code", 0);
		return map;
	}
}
