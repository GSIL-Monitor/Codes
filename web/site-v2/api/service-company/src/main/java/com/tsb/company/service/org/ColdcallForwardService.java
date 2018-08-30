package com.tsb.company.service.org;

import java.util.List;

import com.tsb.company.vo.ColdcallForwardVO;
import com.tsb.company.vo.UserVO;

public interface ColdcallForwardService {
	List<UserVO> getCollegues(int userId);
	List<ColdcallForwardVO> getForwards(Integer coldcallId);
	void forward(Integer coldcallId,Integer fromUserId,Integer toUserId);

	
}
