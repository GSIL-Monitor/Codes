package com.tsb.admin.dao;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.admin.vo.AvgPreScoreVO;
import com.tsb.admin.vo.DemodayCompanyVO;
import com.tsb.admin.vo.DemodayOrgVO;
import com.tsb.admin.vo.UserPreScoreVO;

public interface DemodayVOReadDao {
	// 包括参加和不参加的
	List<DemodayOrgVO> getDemodayOrgVOList(Integer demodayId);

	List<DemodayCompanyVO> getDemodayCompanyVOList(Integer demodayId);

	List<AvgPreScoreVO> getCompaniesAvgPreScore(Integer dealDemodayId);

	// 查询所有合伙人打分
	List<UserPreScoreVO> getPartnerPreScores(Integer dealDemodayId);

	// 查询所有人打分
	List<UserPreScoreVO> getAllUserPreScores(Integer dealDemodayId);

	List<DemodayCompanyVO> getSysDemodayCompanyVOList(@Param("demodayId") Integer demodayId,
			@Param("starst") Integer starst, @Param("pageSize") Integer pageSize,
			@Param("organizationId") Integer organizationId);
	
	List<DemodayCompanyVO> getAllSysDemodayCompanyVO(@Param("demodayId") Integer demodayId,
			@Param("organizationId") Integer organizationId);
}
