package com.tsb.dao.write.demoday;

import com.tsb.model.demoday.DemodayScore;

public interface DemodayScoreWriteDao {
	void insert(DemodayScore demodayScore);

	void update(DemodayScore demodayScore);
	
	void delete (Integer dealDemodayId);
}
