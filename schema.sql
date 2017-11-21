
-- Create a small table for queueing purposes

create table signqueue (
	  id integer primary key autoincrement,
	  gpgkey text,
	  document text
);

