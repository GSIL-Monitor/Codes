package com.tsb.company.service.org.impl;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.company.dao.ColdcallVODao;
import com.tsb.company.dao.DealScoreVODao;
import com.tsb.company.service.org.ColdcallForwardService;
import com.tsb.company.service.org.TaskService;
import com.tsb.company.vo.ColdcallVO;
import com.tsb.dao.read.org.OrganizationReadDao;
import com.tsb.dao.read.user.UserReadDao;
import com.tsb.enums.DealType;
import com.tsb.model.user.User;

@Service
@SuppressWarnings({ "rawtypes", "unchecked" })
public class TaskServiceImpl implements TaskService {

	@Autowired
	private OrganizationReadDao organizationReadDao;

	@Autowired
	private ColdcallVODao coldcallVODao;

	@Autowired
	private DealScoreVODao dealScoreVODao;

	@Autowired
	private UserReadDao userReadDao;
	
	@Autowired
	private ColdcallForwardService coldcallForwardService;

	@Override
	public Map countTODO(Integer userId, Integer filter) {

		int organizationId = organizationReadDao.getByUser(userId).getId();
		Map map = new HashMap();
		map.put("cnt_todo_coldcall", coldcallVODao.countTODO(organizationId, userId, filter));
		map.put("cnt_todo_sponsoredcoldcall", coldcallVODao.countTODOSponsored(organizationId, userId, filter));
		map.put("cnt_todo_recommend",
				dealScoreVODao.countTODO(organizationId, userId, DealType.RECOMMEND.getValue(), filter));
		map.put("cnt_todo_self", dealScoreVODao.countTODO(organizationId, userId, DealType.USER.getValue(), filter));
		return map;
	}

	@Override
	public Map getTaskList(Integer userId, Integer filter, Integer from, Integer pageSize, String type) {

		int organizationId = organizationReadDao.getByUser(userId).getId();
		int cnt_todo_coldcall = coldcallVODao.countTODO(organizationId, userId, filter);
		int cnt_todo_recommend = dealScoreVODao.countTODO(organizationId, userId, DealType.RECOMMEND.getValue(),
				filter);

		List list = new ArrayList();
		int cnt_total = 0;
		if (type.equals("all")) {
			list = coldcallVODao.listTasks(organizationId, userId, filter, from, pageSize);
			cnt_total = cnt_todo_coldcall + cnt_todo_recommend;
		} else if (type.equals("coldcall")) {
			list = coldcallVODao.listTODO(organizationId, userId, filter, from, pageSize);
			cnt_total = cnt_todo_coldcall;
		} else {
			list = dealScoreVODao.listTODO(organizationId, userId, DealType.RECOMMEND.getValue(), filter, from,
					pageSize);
			cnt_total = cnt_todo_recommend;
		}
		Map map = new HashMap();
		map.put("cnt_total", cnt_total);
		map.put("list", list);

		return map;
	}

	@Override
	public Map getPublishList(Integer userId, Integer filter, Integer from, Integer pageSize) {

		int organizationId = organizationReadDao.getByUser(userId).getId();
		int cnt_total = coldcallVODao.countTODOSponsored(organizationId, userId, filter);
		List<ColdcallVO> list = coldcallVODao.listTODOSponsored(organizationId, userId, filter, from, pageSize);
		for (ColdcallVO vo : list) {
			if (vo.getAssigneeId() != null) {
				User user = userReadDao.getById(vo.getAssigneeId());
				vo.setAssignee(user.getUsername());
			}
			if (vo.getSponsorId() != null) {
				User user = userReadDao.getById(vo.getSponsorId());
				vo.setSponsor(user.getUsername());
			}
			// get forwards list
			vo.setForwards(coldcallForwardService.getForwards(vo.getColdcallId()));
		}
		Map map = new HashMap();
		map.put("cnt_total", cnt_total);
		map.put("list", list);
		return map;
	}

	@Override
	public Map getSelfList(Integer userId, Integer filter, Integer from, Integer pageSize) {

		int organizationId = organizationReadDao.getByUser(userId).getId();
		int cnt_total = dealScoreVODao.countTODO(organizationId, userId, DealType.USER.getValue(), filter);
		List list = dealScoreVODao.listTODO(organizationId, userId, DealType.USER.getValue(), filter, from, pageSize);

		Map map = new HashMap();
		map.put("cnt_total", cnt_total);
		map.put("list", list);
		return map;
	}

}
