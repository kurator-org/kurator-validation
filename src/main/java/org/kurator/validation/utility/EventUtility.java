/** EventUtility.java
 *
 * Copyright 2016 President and Fellows of Harvard College
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.kurator.validation.utility;

import java.text.ParsePosition;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.Period;
import java.time.Year;
import java.time.YearMonth;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.time.temporal.ChronoField;
import java.time.temporal.Temporal;
import java.time.temporal.TemporalAccessor;
import java.time.temporal.TemporalField;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

/**
 * @author mole
 *
 */
public class EventUtility {
	
	/**
	 * 
	 */
	public static final String ISO_DATE_TIME = "ISO_DATE_TIME";
	/**
	 * 
	 */
	public static final String RFC_1123_DATE_TIME = "RFC_1123_DATE_TIME";
	/**
	 * 
	 */
	public static final String INTERVAL_ToDayYearOmmitted = "yyyy-mm-dd/[yyyy-]mm-dd";
	/**
	 * 
	 */
	public static final String INTERVAL_ToDayYearMonthOmitted = "yyyy-mm-dd/[yyyy-mm-]dd";
	/**
	 * 
	 */
	public static final String INTERVAL_ToMonthYearOmmitted = "yyyy-mm/[yyyy-]mm";
	public static final String INTERVAL_PERIOD = "yyyy-mm-dd/P";
	public static final String INTERVAL_RECURRINGPERIOD = "yyyy-mm-dd/RP";
	public static final String INTERVAL  = "INTERVAL";
	public static final String ISO_DATE  = "yyyy-mm-dd";
	public static final String ISO_MONTH = "yyyy-mm";
	public static final String ISO_YEAR  = "yyyy";
	public static final String RFC3339_DATETIME = "yyyy-mm-ddThh:mm:ssZ";

	/**
	 * Test for a measure of quality, does an eventDate have 
	 * a non-empty value.  Does not test if content has the
	 * format for a date.
	 * 
	 * @param eventDate value to test.
	 * @return true if event date is not null and not blank.
	 */
	public static boolean eventDatePopulated(String eventDate) {
		boolean result = false;
		if (eventDate!=null) { 
			result = eventDate.trim().length()>0;
		}
		return result; 
	}
	
	/**
	 * Test for a measure of quality, does an event date specify
	 * a date to the precision of one day.
	 * 
	 * @param eventDate
	 * @return
	 */
	public static boolean eventDateSingleDay(String eventDate) { 
		boolean result = false;
		if (EventUtility.eventDateExists(eventDate)) { 
			List<String>components = EventUtility.splitDateRange(eventDate);
			if (components.size()==1) { 
				try {
				    LocalDate.parse(eventDate);
				    result = true;
				} catch (DateTimeParseException e) { } 
			} else if (components.size()>1) {
				try {
				   LocalDate startDate = LocalDate.parse(components.get(0));
				   LocalDate endDate = LocalDate.parse(components.get(components.size()-1));
				   if (startDate.isEqual(endDate)) { 
					   result = true;
				   }
				} catch (DateTimeParseException e) { } 
			}
		}
		return result;
	}
	
	/**
	 * Test for a measure of quality, does an eventDate precede
	 * the earliest adoption of the Gregorian calendar.  
	 * 
	 * @param eventDate value to test.
	 * @return true if event date includes an element prior to 1582-October-15.
	 */
	public static boolean eventDateInProlepticGregorianRange(String eventDate) {
		return true; 
	}
	
	/**
	 * Test for a measure of quality, does an eventDate fall after
	 * the adoption of the Gregorian calendar in the British empire.  
	 * In biodiversity data, dates earlier than this date are unlikely. 
	 * 
	 * @param eventDate value to test.
	 * @return true if event date falls entirely after 1752-September-14
	 */
	public static boolean eventDateInBritishGregorianRange(String eventDate) {
		return false; 
	}
	
	/**
	 * Test for a measure of quality, does an eventDate fall after
	 * the adoption of the Gregorian calendar by Russia.  
	 * 
	 * @param eventDate value to test.
	 * @return true if event date falls entirely after 1900-January-7
	 */
	public static boolean eventDateInRussianGregorianRange(String eventDate) {
		return false; 
	}
	/**
	 * Test for measure of quality, does an event date specify
	 * a date to within a single year.
	 * 
	 * @param eventDate
	 * @return
	 */
	public static boolean eventDateWithinOneYear(String eventDate) {
		boolean result = false;
		if (EventUtility.eventDateExists(eventDate)) { 
			List<String>components = EventUtility.splitDateRange(eventDate);
			if (components.size()==1) { 
				try {
				    Year.parse(eventDate.substring(0, 4));
				    result = true;
				} catch (DateTimeParseException e) { } 
			} else if (components.size()>1) {
				try {
				   Year startDate = Year.parse(components.get(0).substring(0,4));
				   Year endDate = Year.parse(components.get(components.size()-1).substring(0,4));
				   if (!startDate.isAfter(endDate) && !startDate.isBefore(endDate)) { 
					   result = true;
				   }
				} catch (DateTimeParseException e) { 
					e.printStackTrace();
				} 
			}
		} else { 
			String format = EventUtility.identifyDateFormat(eventDate);
			if (format!=null && ( 
					format.equals(EventUtility.RFC3339_DATETIME) || 
					format.equals(RFC_1123_DATE_TIME) || 
					format.equals(EventUtility.ISO_DATE_TIME)) 
			){
				// not an interval, should have year first, try extracting the year.
				try { 
				    Year.parse(eventDate.substring(0,4));
				    result = true;
				} catch (DateTimeParseException e) { }
			}
		}
		return result;
	}	
	
    /**
	 * validation: eventDate format conforms to ISO date format.
     * 
     * @param EventDate
     * @return
     */
	public static boolean eventDateStandardFormat(String eventDate) {
		boolean result = false;
		if (EventUtility.eventDatePopulated(eventDate)) { 
			try {
			if(EventUtility.identifyDateFormat(eventDate)!=null) { 
				if (EventUtility.identifyDateFormat(eventDate).equals(EventUtility.INTERVAL)) { 
					String[] bits = eventDate.split("/");
					if (EventUtility.identifyDateFormat(bits[0])!=null && EventUtility.identifyDateFormat(bits[1])!=null) { 
						result = true;
					}
				} else if (EventUtility.identifyDateFormat(eventDate).equals(EventUtility.INTERVAL_PERIOD)) {
					if (splitDateRange(eventDate)!=null && splitDateRange(eventDate).size()==2) { 
						result = true;
					}
				} else { 
					result = true;
				}
			}
			} catch (DateTimeParseException e) { }
		}
	    return result;
    }
	
	/**
	 * validation: eventDate contains a valid date or date range (e.g. not 1990-Feb-31).
	 * 
	 * @param EventDate
	 * @return
	 */
	public static boolean eventDateExists(String eventDate) {
		boolean result = false;
	    if (EventUtility.eventDateStandardFormat(eventDate)) { 
	    	String format = EventUtility.identifyDateFormat(eventDate);
	    	if (format.equals(EventUtility.ISO_DATE)) {
	    		try { 
	    		   LocalDate.parse(eventDate);
	    		   result = true;
	    		} catch (Exception e) {} 
	    	}
	    	if (format.equals(EventUtility.ISO_YEAR)) {
	    		try { 
	    		   Year.parse(eventDate);
	    		   result = true;
	    		} catch (Exception e) {} 
	    	}
	    	if (format.equals(EventUtility.ISO_MONTH)) {
	    		try { 
	    		   YearMonth.parse(eventDate);
	    		   result = true;
	    		} catch (Exception e) {} 
	    	}
	    	if (format.equals(ISO_DATE_TIME) || format.equals("")) {
	    		try { 
	    		   ZonedDateTime.parse(eventDate);
	    		   result = true;
	    		} catch (Exception e) {} 
	    	}
	    	if (format.equals(EventUtility.INTERVAL) || 
	    			format.equals(EventUtility.INTERVAL_PERIOD) || 
	    			format.equals(EventUtility.INTERVAL_ToDayYearMonthOmitted) ||
	    			format.equals(EventUtility.INTERVAL_ToDayYearOmmitted)
	    			) {
	    		try { 
	    		   List<String> splits = EventUtility.splitDateRange(eventDate);
	    		   if (splits.size()==2) { 
	    		       LocalDate.parse(splits.get(0));
	    		       LocalDate.parse(splits.get(1));
	    		       result = true;
	    		   }
	    		} catch (Exception e) {} 
	    	}
	    	if (format.equals(EventUtility.INTERVAL_ToMonthYearOmmitted)) {
	    		try { 
	    		   List<String> splits = EventUtility.splitDateRange(eventDate);
	    		   if (splits.size()==2) { 
	    		       YearMonth.parse(splits.get(0));
	    		       YearMonth.parse(splits.get(1));
	    		       result = true;
	    		   }
	    		} catch (Exception e) { } 
	    	}	    	
	    }
	    return result;
    }

	/**
	 * validation: eventDate is consistent with day, month, year, startDayOfYear, endDatOfYear.  
	 * 
	 * @param EventDate
	 * @param year
	 * @param month
	 * @param day
	 * @param startDayOfYear
	 * @param endDayOfYear
	 * @return
	 */
	public static boolean eventInternallyConsistent(String EventDate, Integer year, Integer month, Integer day, Integer startDayOfYear, Integer endDayOfYear) { 
	    return false;
    }

	/**
	 * validation: eventDate is consistent with verbatimEventDate  
	 * 
	 * @param EventDate
	 * @param year
	 * @param month
	 * @param day
	 * @param startDayOfYear
	 * @param endDayOfYear
	 * @return
	 */
	public static boolean eventDateVerbatimDateConsistent(String EventDate, Integer year, Integer month, Integer day, Integer startDayOfYear, Integer endDayOfYear) { 
	    return false;
    }

	
	

	//TODO: enhancement: populate an empty eventDate from day, month, year, and/or verbatimEventDate	
	public static String assembleEventDate(Integer year, Integer month, Integer day, Integer startDayOfYear, Integer endDayOfYear) {
		return null;
	}
	
	/**
	 * Given a string that may represent a date or a date range,
	 * split into beginning and end dates.  Input order is preserved,
	 * no attempt is made to check if beginning date is before end date. 
	 * 
	 * @param date a string that may contain an ISO date or date range
	 * @return a list containing date if date does not contain one /
	 * otherwise a list of two parts of date split on /.  
	 */
	public static List<String> splitDateRange(String date) { 
		ArrayList<String> result = new ArrayList<String>();
		if (date.matches("^[-0-9]+/[-0-9]+$")) {
			String[] splits = date.split("/");
			if (splits.length==2) { 
				String[] startBits = splits[0].split("-");
				String[] endBits = splits[1].split("-");
				String fullFormat = identifyDateFormat(date);
				String format = identifyDateFormat(splits[0]);
				if (format!=null && format.equals(EventUtility.ISO_DATE)) { 
					ArrayList<String> newEndBits = new ArrayList<String>();
					if (endBits[0].length()==2) { 
						if (endBits.length==1) { 
							for (int i=0; i<startBits.length-1; i++) {
								newEndBits.add(startBits[i]);
							}
							newEndBits.add(endBits[0]);
							endBits = newEndBits.toArray(new String[0]);
						} else if (endBits.length==2) { 
							for (int i=0; i<(startBits.length-2); i++) {
								newEndBits.add(startBits[i]);
							}
							newEndBits.add(endBits[0]);
							newEndBits.add(endBits[1]);
							endBits = newEndBits.toArray(new String[0]);							
						}
						StringBuffer endDate = new StringBuffer();
						String separator = "";
						for (int i=0; i<endBits.length; i++) {
							endDate.append(separator).append(endBits[i]);
							separator = "-";
						}
						splits[1] = endDate.toString();
					}
				} else if (fullFormat !=null && fullFormat.equals(EventUtility.INTERVAL_ToMonthYearOmmitted)) { 
					splits[1] = splits[0].substring(0,4) + '-' + splits[1];
				}
			}
			result.addAll(Arrays.asList(splits));
		} else { 
			if (date.contains("P")) { 
				if (date.matches("^[-0-9]+/[-0-9PDWMY]+$")) { 
					String[] splits = date.split("/");
					if (splits.length==2) {
						if (identifyDateFormat(splits[0])==EventUtility.ISO_DATE) {
					        LocalDate dateOne = LocalDate.parse(splits[0]);
					        if (splits[1].matches("P[0-9]+D")) { 
					        	splits[1] = dateOne.plusDays(Integer.parseInt(splits[1].replaceAll("[^0-9]", ""))).toString();
					        }
					        if (splits[1].matches("P[0-9]+M")) { 
					        	splits[1] = dateOne.plusMonths(Integer.parseInt(splits[1].replaceAll("[^0-9]", ""))).toString();
					        }					        
					        if (splits[1].matches("P[0-9]+Y")) { 
					        	splits[1] = dateOne.plusYears(Integer.parseInt(splits[1].replaceAll("[^0-9]", ""))).toString();
					        }					        
					        if (splits[1].matches("P[0-9]+W")) { 
					        	splits[1] = dateOne.plusWeeks(Integer.parseInt(splits[1].replaceAll("[^0-9]", ""))).toString();
					        }
					        if (splits[1].matches("P0000-00-[0-9]{2}")) { 
					        	String[] periodSplit = splits[1].split("-");
					        	String days = periodSplit[periodSplit.length-1];
					        	splits[1] = dateOne.plusDays(Integer.parseInt(days)).toString();
					        } else { 
					        }
						    	
						}
					}
					result.addAll(Arrays.asList(splits));
				} else if (date.matches("[-0-9PDMY]+/[-0-9]+")) { 
					String[] splits = date.split("/");
					Period.parse(splits[1]);
				    	
				} else { 
					String[] splits = date.split("/");
					if (splits.length==2) {
						if (identifyDateFormat(splits[0])==EventUtility.ISO_DATE) {
					        LocalDate dateOne = LocalDate.parse(splits[0]);
					        Period p = Period.parse(splits[1]);
						    splits[1] = dateOne.plus(p).toString(); 
						    result.addAll(Arrays.asList(splits));
					    }  
					}
				}
			} else { 
			    result.add(date);
			}
		}
		return result;
	}
	
	public static String identifyDateFormat(String date) { 
		ParsePosition position = new ParsePosition(0);
		if (date==null || date.trim().length()==0) { 
			return null;
		}
		//Date parsed = DateFormat.getInstance().parse(date, position);
		String match = null;
		if (date.matches("^[0-9]{4}[-0-9]*/[-0-9]+$")) { 
			match = EventUtility.INTERVAL;
			if (date.matches("^[0-9]{4}-[0-9]{2}/[0-9]{2}$")) {
				match = INTERVAL_ToMonthYearOmmitted;
			}
			if (date.matches("^[0-9]{4}-[0-9]{2}-[0-9]{2}/[0-9]{2}$")) {
				match = INTERVAL_ToDayYearMonthOmitted;
			}
			if (date.matches("^[0-9]{4}-[0-9]{2}-[0-9]{2}/[0-9]{2}-[0-9]{2}$")) {
				match = INTERVAL_ToDayYearOmmitted;
			}
			String[] bits = date.split("/");
			if (!match.equals(EventUtility.INTERVAL)) { 
				if (match.equals(INTERVAL_ToMonthYearOmmitted)) { 
					bits[1] = bits[0].substring(0, 4) + '-' + bits[1];
				}
				if (match.equals(INTERVAL_ToDayYearMonthOmitted)) { 
					bits[1] = bits[0].substring(0, 8) + bits[1];
				}
				if (match.equals(INTERVAL_ToDayYearOmmitted)) { 
					bits[1] = bits[0].substring(0, 4) + '-' + bits[1];
				}
			}
			TemporalAccessor tStart = getLocalDateFromString(bits[0]);
			TemporalAccessor tEnd = getLocalDateFromString(bits[1]);
			if (LocalDate.from(tStart).isAfter(LocalDate.from(tEnd))) {
				// Start date must be before end date.
				return null;
			}
		} else if (date.matches("^[0-9]{4}[-0-9]*/R[0-9]+[Pp][0-9YMDW]+$")) {
		    match = EventUtility.INTERVAL_RECURRINGPERIOD;
		} else if (date.matches("^[0-9]{4}[-0-9]*/[Pp][0-9YMDW]+$")) {
			match = EventUtility.INTERVAL_PERIOD;
		} else if (date.matches("^[0-9]{4}[-0-9]*/[Pp][-0-9]+$")) {
			match = EventUtility.INTERVAL_PERIOD;
		} else { 
			if (date.matches("^[0-9]{4}$")) { 
				match = EventUtility.ISO_YEAR;
			}
			if (date.matches("^[0-9]{4}-[0-9]{2}$")) { 
				match = EventUtility.ISO_MONTH;
			}
			if (date.matches("^[0-9]{4}-[0-9]{2}-[0-9]{2}$")) { 
			try {
				DateTimeFormatter.ISO_DATE.parseUnresolved(date, position).getClass();
				// check for yyyy-00-dd or yyyy-mm-00 or yyyy-00-00 as parseUnresolved accepts these.
				if (!date.matches(".*-00.*")) { 
					match = EventUtility.ISO_DATE;
				}
			} catch (Exception e) {} 
			}
			try {
				DateTimeFormatter.ISO_DATE_TIME.parseUnresolved(date, position).getClass();
				match = ISO_DATE_TIME;
			} catch (Exception e) {} 
			try {
				DateTimeFormatter.ISO_ORDINAL_DATE.parseUnresolved(date, position).getClass();
				// check for yyyy-ddd, as parseUnresolved will match on yyyy-nnnn.
				if (date.matches("^[0-9]{4}-[0-3][0-9]{2}$")) { 
					match = "ISO_ORDINAL_DATE";
				}
			} catch (Exception e) {} 
			if (date.matches("^[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt ][012][0-9]:[0-6][0-9]:[0-6][0-9][Zz]$")) {
				match = EventUtility.RFC3339_DATETIME;
			}
			try {
				DateTimeFormatter.RFC_1123_DATE_TIME.parseUnresolved(date, position).getClass();
				match = EventUtility.RFC_1123_DATE_TIME;
			} catch (Exception e) {} 
			try {
				DateTimeFormatter.ISO_WEEK_DATE.parseUnresolved(date, position).getClass();
				match = "ISO_WEEK_DATE";
			} catch (Exception e) {} 
		} 
		if (position.getIndex()>0 && position.getIndex()<date.length()) {

		}
		return match;
	}
	
	public static LocalDate getLocalDateFromString(String date) throws DateTimeParseException {
		Temporal working = null;
		LocalDate result = null;
		try {
			result = LocalDate.parse(date);
		} catch (DateTimeParseException e) { 
			try {
				working = java.time.Year.parse(date);
				result = LocalDate.of(working.get(ChronoField.YEAR), 1, 1);
			} catch (DateTimeParseException e1) { 
				try {
					working = java.time.YearMonth.parse(date);
					result = LocalDate.of(working.get(ChronoField.YEAR),working.get(ChronoField.MONTH_OF_YEAR),1);
				} catch (DateTimeParseException e2) { 
						result = LocalDateTime.parse(date).toLocalDate();
				}
			}
		}
		return result;
	}
	
}
