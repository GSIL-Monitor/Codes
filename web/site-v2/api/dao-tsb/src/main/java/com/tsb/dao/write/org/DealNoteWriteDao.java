package com.tsb.dao.write.org;

import com.tsb.model.org.user.DealNote;

public interface DealNoteWriteDao {
	void insert(DealNote dealNote);
	void update(DealNote dealNote);
	void delete(Integer id);
	
}
