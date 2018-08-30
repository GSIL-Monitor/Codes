package com.tsb.company.dao;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.company.vo.DemodayAllUserScoreVO;
import com.tsb.company.vo.DemodayCompanyVO;
import com.tsb.company.vo.DemodayOrgResultVO;
import com.tsb.company.vo.DemodayPreScoreVO;
import com.tsb.company.vo.DemodayScoreVO;

public interface DemodayVODao {
	List<DemodayPreScoreVO> getPreScores(@Param("userId") Integer userId, @Param("demodayId") Integer demodayId,
			@Param("status") Integer status);

	List<DemodayScoreVO> getScores(@Param("userId") Integer userId, @Param("demodayId") Integer demodayId);

	List<DemodayAllUserScoreVO> getAllUserScore(@Param("companyId") Integer companyId,
			@Param("dealDemodayId") Integer dealDemodayId);

	List<DemodayOrgResultVO> getOrgResults(@Param("demodayCompanyId") Integer demodayCompanyId,
			@Param("demodayId") Integer demodayId);

	List<String> getJoinDemodayOrgs(@Param("demodayId") Integer demodayId, @Param("status") Integer status);

	List<String> getNotJoinOrgs(@Param("demodayId") Integer demodayId, @Param("status") Integer status);

	List<DemodayCompanyVO> getDemodayCompanies(Integer demodayId);

	List<DemodayPreScoreVO> getNotPassedList(@Param("start") Integer start, @Param("pageSize") Integer pageSize,
			@Param("userId") Integer userId, @Param("demodayId") Integer demodayId);
}
