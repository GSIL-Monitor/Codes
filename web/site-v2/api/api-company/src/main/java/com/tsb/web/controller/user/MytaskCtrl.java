package com.tsb.web.controller.user;

import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.company.service.org.TaskService;
import com.tsb.util.RequestVO;
import com.tsb.web.controller.BaseController;

@Controller
@RequestMapping(value = "/api/company/mytask")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class MytaskCtrl extends BaseController {
	
	@Autowired
	private TaskService taskService;

	@RequestMapping(value = "/counttodo", method=RequestMethod.POST)
	@ResponseBody
	public Object countTODO(@RequestBody RequestVO request) {
		int userId = request.getUserid();
		//filter 为0
		Map map=taskService.countTODO(userId, 0);
		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/task/list", method=RequestMethod.POST)
	@ResponseBody
	public Object getTasks(@RequestBody RequestVO request) {
		int userId = request.getUserid();
		String type = (String)request.getPayload().get("type");
		int filter = (int)request.getPayload().get("filter");
		int from = (int)request.getPayload().get("from");
		int pageSize = 10;
		Map map=taskService.getTaskList(userId, filter, from, pageSize, type);
		map.put("code", 0);
		return map;
	}
	
	
	
	@RequestMapping(value = "/publish/list", method=RequestMethod.POST)
	@ResponseBody
	public Object listSponsoredColdcall(@RequestBody RequestVO request) {
		int userId = request.getUserid();
		int filter = (int)request.getPayload().get("filter");
		int from = (int)request.getPayload().get("from");
		int pageSize = 10;
		Map map=taskService.getPublishList(userId, filter, from, pageSize);
		map.put("code", 0);
		return map;
	}
	
	
	@RequestMapping(value = "/self/list", method=RequestMethod.POST)
	@ResponseBody
	public Object listself(@RequestBody RequestVO request) {
		int userId = request.getUserid();
		int filter = (int)request.getPayload().get("filter");
		int from = (int)request.getPayload().get("from");
		int pageSize = 10;
		Map map=taskService.getSelfList(userId, filter, from, pageSize);
		map.put("code", 0);
		return map;
	}
	

//	@RequestMapping(value = "/listcoldcall", method=RequestMethod.POST)
//	@ResponseBody
//	public Object listColdcall(@RequestBody RequestVO request) {
//		int userId = request.getUserid();
//		int filter = (int)request.getPayload().get("filter");
//		int from = (int)request.getPayload().get("from");
//		int pageSize = 10;
//		
//		Organization org = organizationReadDao.getByUser(userId);
//		int organizationId = org.getId();
//		
//		int cnt_total = coldcallVODao.countTODO(organizationId, userId,filter);
//		List<ColdcallVO> list = coldcallVODao.listTODO(organizationId, userId, filter, from, pageSize);
//		for(ColdcallVO vo : list){
//			if( vo.getAssigneeId() != null){
//				User user = userReadDao.getById(vo.getAssigneeId());
//				vo.setAssignee(user.getUsername());
//			}
//			if( vo.getSponsorId() != null){
//				User user = userReadDao.getById(vo.getSponsorId());
//				vo.setSponsor(user.getUsername());
//			}
//		}
//		Map map = new HashMap();
//		map.put("cnt_total", cnt_total);
//		map.put("list", list);
//		map.put("code", 0);
//		return map;
//	}
//	
//	
//	@RequestMapping(value = "/listcoldcalldeclined", method=RequestMethod.POST)
//	@ResponseBody
//	public Object listColdcallDeclined(@RequestBody RequestVO request) {
//		int userId = request.getUserid();
//		int from = (int)request.getPayload().get("from");
//		int pageSize = 10;
//		
//		Organization org = organizationReadDao.getByUser(userId);
//		int organizationId = org.getId();
//		
//		int cnt_total = coldcallVODao.countDeclined(organizationId, userId);
//		List<ColdcallVO> list = coldcallVODao.listDeclined(organizationId, userId, from, pageSize);
//		for(ColdcallVO vo : list){
//			if( vo.getAssigneeId() != null){
//				User user = userReadDao.getById(vo.getAssigneeId());
//				vo.setAssignee(user.getUsername());
//			}
//			if( vo.getSponsorId() != null){
//				User user = userReadDao.getById(vo.getSponsorId());
//				vo.setSponsor(user.getUsername());
//			}
//		}
//		Map map = new HashMap();
//		map.put("cnt_total", cnt_total);
//		map.put("list", list);
//		map.put("code", 0);
//		return map;
//	}
//	
//	
//	@RequestMapping(value = "/listsponsoredcoldcalldeclined", method=RequestMethod.POST)
//	@ResponseBody
//	public Object listSponsoredColdcallDeclined(@RequestBody RequestVO request) {
//		int userId = request.getUserid();
//		int from = (int)request.getPayload().get("from");
//		int pageSize = 10;
//		
//		Organization org = organizationReadDao.getByUser(userId);
//		int organizationId = org.getId();
//		
//		int cnt_total = coldcallVODao.countSponsoredDeclined(organizationId, userId);
//		List<ColdcallVO> list = coldcallVODao.listSponsoredDeclined(organizationId, userId, from, pageSize);
//		for(ColdcallVO vo : list){
//			if( vo.getAssigneeId() != null){
//				User user = userReadDao.getById(vo.getAssigneeId());
//				vo.setAssignee(user.getUsername());
//			}
//			if( vo.getSponsorId() != null){
//				User user = userReadDao.getById(vo.getSponsorId());
//				vo.setSponsor(user.getUsername());
//			}
//		}
//		Map map = new HashMap();
//		map.put("cnt_total", cnt_total);
//		map.put("list", list);
//		map.put("code", 0);
//		return map;
//	}
//	
//	@RequestMapping(value = "/listrecommend", method=RequestMethod.POST)
//	@ResponseBody
//	public Object listRecommend(@RequestBody RequestVO request) {
//		int userId = request.getUserid();
//		int filter = (int)request.getPayload().get("filter");
//		int from = (int)request.getPayload().get("from");
//		int pageSize = 10;
//		
//		Organization org = organizationReadDao.getByUser(userId);
//		int organizationId = org.getId();
//		
//		int cnt_total = dealScoreVODao.countTODO(organizationId, userId, 23030, filter);
//		List list = dealScoreVODao.listTODO(organizationId, userId, 23030, filter, from, pageSize);
//		
//		Map map = new HashMap();
//		map.put("cnt_total", cnt_total);
//		map.put("list", list);
//		map.put("code", 0);
//		return map;
//	}
}
