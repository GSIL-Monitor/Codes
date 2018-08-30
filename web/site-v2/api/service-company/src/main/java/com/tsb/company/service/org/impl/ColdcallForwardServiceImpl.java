package com.tsb.company.service.org.impl;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.company.dao.UserVODao;
import com.tsb.company.service.org.ColdcallForwardService;
import com.tsb.company.vo.ColdcallForwardVO;
import com.tsb.company.vo.UserVO;
import com.tsb.dao.read.org.ColdcallForwardReadDao;
import com.tsb.dao.read.org.user.ColdcallUserRelReadDao;
import com.tsb.dao.read.user.UserReadDao;
import com.tsb.dao.write.org.ColdcallForwardWriteDao;
import com.tsb.dao.write.org.user.ColdcallUserRelWriteDao;
import com.tsb.model.org.ColdcallForward;
import com.tsb.model.org.user.ColdcallUserRel;
import com.tsb.model.user.User;

@Service
public class ColdcallForwardServiceImpl implements ColdcallForwardService {

	@Autowired
	private UserVODao userVODao;
	@Autowired
	private ColdcallForwardWriteDao coldCallForwardWriteDao;
	@Autowired
	private ColdcallForwardReadDao coldcallForwardReadDao;
	@Autowired
	private UserReadDao userReadDao;
	@Autowired
	private ColdcallUserRelReadDao coldcallUserRelReadDao;
	@Autowired
	private ColdcallUserRelWriteDao coldcallUserRelWriteDao;

	@Override
	public List<UserVO> getCollegues(int userId) {
		List<UserVO> list = userVODao.getCollegues(userId);
		List<UserVO> collegues = new ArrayList<UserVO>();
		for (UserVO user : list) {
			if (user.getId() != userId)
				collegues.add(user);
		}
		return collegues;
	}

	@Override
	public void forward(Integer coldcallId, Integer fromUserId, Integer toUserId) {
		
		ColdcallForward old = coldcallForwardReadDao.getColdcallForward(coldcallId, fromUserId, toUserId);
		if (null != old) {
			return;
		} else {
			
			Timestamp time = new Timestamp(System.currentTimeMillis());
			ColdcallForward ccf = new ColdcallForward();
			ccf.setColdcallId(coldcallId);
			ccf.setFromUserId(fromUserId);
			ccf.setToUserId(toUserId);
			coldCallForwardWriteDao.insert(ccf);
			
			ColdcallUserRel ccUserRel=coldcallUserRelReadDao.get(coldcallId, fromUserId);
			ccUserRel.setUserId(toUserId);
			//21020--assignee
			ccUserRel.setUserIdentify(21020);
			ccUserRel.setModifyTime(time);
			coldcallUserRelWriteDao.update(ccUserRel);
		}

	}

	@Override
	public List<ColdcallForwardVO> getForwards(Integer coldcallId) {
			List<ColdcallForward> forwardList = coldcallForwardReadDao.get(coldcallId);
			if (null != forwardList && !forwardList.isEmpty()) {
				List<ColdcallForwardVO> forwards = new ArrayList<ColdcallForwardVO>();
				for (ColdcallForward ccf : forwardList) {
					ColdcallForwardVO forward = new ColdcallForwardVO();
					if(null!=ccf.getFromUserId()&&0!=ccf.getFromUserId()){
						User fromUser = userReadDao.getById(ccf.getFromUserId());
						forward.setFromUserName(fromUser.getUsername());
					}
					if(null!=ccf.getToUserId()&&0!=ccf.getToUserId()){
						User toUser = userReadDao.getById(ccf.getToUserId());
						forward.setToUserName(toUser.getUsername());
					}
					forwards.add(forward);
				}
				return forwards;
			} else {
				return null;
			}
	}

}
