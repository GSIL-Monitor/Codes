package com.tsb.company.service.impl;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.company.service.MemberService;
import com.tsb.company.vo.MemberVO;
import com.tsb.dao.read.company.CompanyMemberRelReadDao;
import com.tsb.dao.read.company.MemberReadDao;
import com.tsb.dao.write.company.CompanyMemberRelWriteDao;
import com.tsb.dao.write.company.MemberWriteDao;
import com.tsb.model.company.CompanyMemberRel;
import com.tsb.model.company.Member;

@Service
public class MemberServiceImpl implements MemberService {
	
	@Autowired
	private CompanyMemberRelReadDao cmrReadDao;
	
	@Autowired
	private MemberReadDao memberReadDao;
	
	@Autowired
	private MemberWriteDao memberWriteDao;

	@Autowired
	private CompanyMemberRelWriteDao cmrWriteDao;

	@Override
	public List<MemberVO> getMembers(Integer id) {
		List<CompanyMemberRel> cmrList = cmrReadDao.get(id);
		List<MemberVO> mVOList = new ArrayList<MemberVO>();
		if (null != cmrList && !cmrList.isEmpty()) {
			List<Integer> memberIds = new ArrayList<Integer>();
			for (CompanyMemberRel cmr : cmrList) {
				MemberVO mVO = new MemberVO();
				mVO.setCompanyMemberRel(cmr);
				mVOList.add(mVO);
				memberIds.add(cmr.getMemberId());
			}
			List<Member> memberList = memberReadDao.getByIds(memberIds);
			Map<Integer, Member> map = new HashMap<Integer, Member>();
			for (Member member : memberList) {
				map.put(member.getId(), member);
			}
			for (MemberVO memberVO : mVOList) {
				memberVO.setMember(map.get(memberVO.getCompanyMemberRel().getMemberId()));
			}
		}
		return mVOList;

	}
	
	
	@Override
	public void addCompanyMember(Member member, Integer companyId, Integer userId) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		// member
		if (member.getName()!=null && !"".equals(member.getName().trim())) {
			member.setCreateTime(time);
			member.setActive('Y');
			member.setVerify('Y');
			member.setCreateUser(userId);
			memberWriteDao.insert(member);
			// company-member-rel
			CompanyMemberRel companyMemberRel = new CompanyMemberRel();
			companyMemberRel.setCompanyId(companyId);
			companyMemberRel.setMemberId(member.getId());
			companyMemberRel.setPosition("创始人");
			companyMemberRel.setType(5010);
			companyMemberRel.setActive('Y');
			companyMemberRel.setCreateUser(userId);
			companyMemberRel.setCreateTime(time);
			cmrWriteDao.insert(companyMemberRel);

		}

	}

}
