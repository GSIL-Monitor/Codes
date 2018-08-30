package com.tsb.admin.service.impl;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.admin.dao.read.CompanyMemberRelReadDao;
import com.tsb.admin.dao.read.MemberReadDao;
import com.tsb.admin.dao.read.source.SourceCompanyMemberRelReadDao;
import com.tsb.admin.dao.read.source.SourceMemberReadDao;
import com.tsb.admin.dao.write.CompanyMemberRelWriteDao;
import com.tsb.admin.dao.write.MemberWriteDao;
import com.tsb.admin.service.MemberService;
import com.tsb.admin.vo.MemberVO;
import com.tsb.admin.vo.SourceMemberVO;
import com.tsb.model.CompanyMemberRel;
import com.tsb.model.Member;
import com.tsb.model.source.SourceCompanyMemberRel;
import com.tsb.model.source.SourceMember;

@Service
public class MemberSerivceImpl implements MemberService {
	
	@Autowired
	private MemberReadDao memberReadDao;
	@Autowired
	private CompanyMemberRelReadDao companyMemberRelReadDao;
	@Autowired
	private SourceMemberReadDao sourceMemberReadDao;
	@Autowired
	private SourceCompanyMemberRelReadDao sourceCompanyMemberRelReadDao;
	@Autowired
	private MemberWriteDao memberWriteDao;
	@Autowired
	private CompanyMemberRelWriteDao companyMemberRelWriteDao;
	
	@Override
	public List<MemberVO> listMemberVOsByCompanyId(Integer id) {
		List<CompanyMemberRel> rels = companyMemberRelReadDao.listByCompanyId(id);
		List<Member> members = memberReadDao.listByCompanyId(id);
		
		List<MemberVO> list = new ArrayList<MemberVO>();
		for(CompanyMemberRel r : rels) {
			MemberVO vo = new MemberVO();
			vo.setRel(r);
			
			for(Member m : members) {
				if(m.getId().intValue() == r.getMemberId().intValue()){
					vo.setMember(m);
					break;
				}
			}
			list.add(vo);
		}
		
		return list;
	}

	@Override
	public List<SourceMemberVO> listSourceMemberVOsByCompanyMemberRelId(
			Integer id) {
		List<SourceMemberVO> list = new ArrayList<SourceMemberVO>();
		List<SourceCompanyMemberRel> rels = sourceCompanyMemberRelReadDao.listByCompanyMemberRelId(id);
		List<SourceMember> members = sourceMemberReadDao.listByCompanyMemberRelId(id);
		
		for(SourceCompanyMemberRel r : rels){
			SourceMemberVO vo = new SourceMemberVO();
			vo.setRel(r);
			
			for(SourceMember m : members){
				if(m.getId().intValue() == r.getSourceMemberId().intValue()){
					vo.setMember(m);
					break;
				}
			}
			
			list.add(vo);
		}
		
		return list;
	}

	@Override
	public void updateMemberAndRel(MemberVO memberVO) {
		Date date = new Date();       
		Timestamp nousedate = new Timestamp(date.getTime());
		
		Member m = memberVO.getMember();
		m.setVerify('Y');
		m.setModifyTime(nousedate);
		memberWriteDao.update(m);	
		
		CompanyMemberRel r = memberVO.getRel();
		r.setVerify('Y');
		r.setModifyTime(nousedate);
		companyMemberRelWriteDao.update(r);
	}

	@Override
	public void deleteCompanyMemberRel(CompanyMemberRel companyMemberRel) {
		Date date = new Date();       
		Timestamp nousedate = new Timestamp(date.getTime());
		
		companyMemberRel.setActive('N');
		companyMemberRel.setModifyTime(nousedate);
		companyMemberRelWriteDao.update(companyMemberRel);
	}

	@Override
	public void addMember(Member m) {
		m.setActive('Y');
		m.setVerify('Y');
		Date date = new Date();       
		Timestamp nousedate = new Timestamp(date.getTime());
		m.setCreateTime(nousedate);
		m.setCreateUser(0);
		memberWriteDao.insert(m);
	}

	@Override
	public void updateMember(Member m) {
		m.setVerify('Y');
		Date date = new Date();       
		Timestamp nousedate = new Timestamp(date.getTime());
		m.setModifyTime(nousedate);
		m.setModifyUser(0);
		memberWriteDao.update(m);
	}

	@Override
	public void deleteMember(Integer id) {
		Member m = memberReadDao.get(id);
		if( m == null){
			return;
		}
		
		Date date = new Date();       
		Timestamp nousedate = new Timestamp(date.getTime());
		
		List<CompanyMemberRel> rels = companyMemberRelReadDao.listByMemberId(id);
		for(CompanyMemberRel r : rels) {
			r.setActive('N');
			r.setModifyTime(nousedate);
			r.setModifyUser(0);
			companyMemberRelWriteDao.update(r);
		}
		
		m.setActive('N');
		m.setModifyTime(nousedate);
		m.setModifyUser(0);
		memberWriteDao.update(m);
	}

}
