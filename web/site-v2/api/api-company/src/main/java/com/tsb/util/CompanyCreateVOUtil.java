package com.tsb.util;

import org.springframework.stereotype.Component;
@Component
public class CompanyCreateVOUtil {
	public String getRoundDesc(Integer round){
		String roundDesc="";
		switch(round){
		case 0: roundDesc="未融资";break;
		case 1010: roundDesc="天使轮";break;
		case 1020:roundDesc="pre-A";break;
		case 1030: roundDesc="A";break;
		case 1031: roundDesc="A+轮";break;
		case 1040:roundDesc="B轮";break;
		case 1050: roundDesc="C轮";break;
		case 1060: roundDesc="D轮以上";break;
		case 1110:roundDesc="IPO";break;
		case 1120:roundDesc="被收购";break;
		default:break;
		}
		return roundDesc;
		
	}
	public Integer parseRound(Integer round) {
		Integer realRound = round;
		if (round == 1031) {
			realRound = 1030;
		}
		return realRound;

	}
}
