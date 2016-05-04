/** EventUtilityTest.java
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

import static org.junit.Assert.*;

import java.util.ArrayList;
import java.util.Arrays;

import org.junit.Test;
import org.kurator.validation.utility.EventUtility;

/**
 * Tests for static utility methods for checking dwc:eventDate and dwc:Event data.
 * 
 * @author mole
 *
 */
public class EventUtilityTest {

	/**
	 * Test method for {@link org.kurator.validation.utility.EventUtility#eventDatePopulated(java.lang.String)}.
	 */
	@Test
	public void testEventDatePopulated() {
		assertEquals(true,EventUtility.eventDatePopulated("1880"));
		assertEquals(true,EventUtility.eventDatePopulated("1880-04"));
		assertEquals(true,EventUtility.eventDatePopulated("1880-04-02"));
		assertEquals(true,EventUtility.eventDatePopulated("9999-99-99"));
		assertEquals(true,EventUtility.eventDatePopulated("0000-00-00"));
		assertEquals(true,EventUtility.eventDatePopulated("1880-04-02/1890-05-02"));
		assertEquals(true,EventUtility.eventDatePopulated("A"));
		assertEquals(true,EventUtility.eventDatePopulated(" A "));
		assertEquals(true,EventUtility.eventDatePopulated(" 1880 "));
		assertEquals(true,EventUtility.eventDatePopulated("0000"));
		
		assertEquals(false,EventUtility.eventDatePopulated(" "));
		assertEquals(false,EventUtility.eventDatePopulated(""));
		assertEquals(false,EventUtility.eventDatePopulated(null));
		assertEquals(false,EventUtility.eventDatePopulated("\t"));
		assertEquals(false,EventUtility.eventDatePopulated("\n"));
	}

	/**
	 * Test method for {@link org.kurator.validation.utility.EventUtility#eventDateSingleDay(java.lang.String)}.
	 */
	@Test
	public void testEventDateSingleDay() {
		assertEquals(true,EventUtility.eventDateSingleDay("1880-01-03"));
		assertEquals(true,EventUtility.eventDateSingleDay("1880-01-03/1880-01-03"));
		assertEquals(true,EventUtility.eventDateSingleDay("0001-01-03")); // Jan 3, year 1.
		assertEquals(true,EventUtility.eventDateSingleDay("9999-01-03"));
		
		assertEquals(false,EventUtility.eventDateSingleDay("1880-31-01"));
		assertEquals(false,EventUtility.eventDateSingleDay("1880"));
		assertEquals(false,EventUtility.eventDateSingleDay("1880-01"));
		assertEquals(false,EventUtility.eventDateSingleDay("1880-01-03/1880-01-04"));
		assertEquals(false,EventUtility.eventDateSingleDay("1880-01-03/1880-02-04"));
		assertEquals(false,EventUtility.eventDateSingleDay("1880-01-03/1881-01-03"));
		
		assertEquals(false,EventUtility.eventDateSingleDay("0000"));
		assertEquals(false,EventUtility.eventDateSingleDay(" "));
		assertEquals(false,EventUtility.eventDateSingleDay(""));
		assertEquals(false,EventUtility.eventDateSingleDay(null));
		assertEquals(false,EventUtility.eventDateSingleDay("\t"));
		assertEquals(false,EventUtility.eventDateSingleDay("\n"));
		assertEquals(false,EventUtility.eventDateSingleDay("21001-01-03"));
	}
	
	@Test
	public void testSplitDateRange() { 		
		assertEquals(Arrays.asList(new String[]{"1880"}), EventUtility.splitDateRange("1880"));
		assertEquals(Arrays.asList(new String[]{"1880","1890"}), EventUtility.splitDateRange("1880/1890"));
		assertEquals(Arrays.asList(new String[]{"1880-02","1890-02"}), EventUtility.splitDateRange("1880-02/1890-02"));
		assertEquals(Arrays.asList(new String[]{"1880-12","1890"}), EventUtility.splitDateRange("1880-12/1890"));
		assertEquals(Arrays.asList(new String[]{"1880-02","1890-02"}), EventUtility.splitDateRange("1880-02/1890-02"));
		assertEquals(Arrays.asList(new String[]{"2012-02","2012-03"}), EventUtility.splitDateRange("2012-02/2012-03"));
		assertEquals(Arrays.asList(new String[]{"1880-02-15","1890-01-28"}), EventUtility.splitDateRange("1880-02-15/1890-01-28"));
		assertEquals(Arrays.asList(new String[]{"1880-02-15","1890"}), EventUtility.splitDateRange("1880-02-15/1890"));
		assertEquals(Arrays.asList(new String[]{"1600-01-15","2100-12-23"}), EventUtility.splitDateRange("1600-01-15/2100-12-23"));
		assertEquals(Arrays.asList(new String[]{"0001","0002"}), EventUtility.splitDateRange("0001/0002"));
		
		// Assumes [0-9]+/[0-9]+ is a range of years, note this isn't a valid date.
		assertEquals(Arrays.asList(new String[]{"1","2"}), EventUtility.splitDateRange("1/2"));
		
		// Order preserved, item before / is returned first
		assertEquals(Arrays.asList(new String[]{"2012-03","2012-02"}), EventUtility.splitDateRange("2012-03/2012-02"));
		
		// for second half of period, leading elements that are the same can be omitted.
		assertEquals(Arrays.asList(new String[]{"2007-11-13","2007-11-15"}),EventUtility.splitDateRange("2007-11-13/15"));   
		assertEquals(Arrays.asList(new String[]{"2007-11-13","2007-12-15"}),EventUtility.splitDateRange("2007-11-13/12-15")); 
		assertEquals(Arrays.asList(new String[]{"2007-11","2007-12"}),EventUtility.splitDateRange("2007-11/12"));   
		
		// Intervals
		assertEquals(Arrays.asList(new String[]{"1883-04-06","1883-04-09"}), EventUtility.splitDateRange("1883-04-06/P3D"));
		assertEquals(Arrays.asList(new String[]{"1880-01-01","1880-01-04"}), EventUtility.splitDateRange("1880-01-01/P3D"));
		assertEquals(Arrays.asList(new String[]{"1883-04-06","1883-04-09"}), EventUtility.splitDateRange("1883-04-06/P0000-00-03"));
		assertEquals(Arrays.asList(new String[]{"1883-04-06","1883-07-06"}), EventUtility.splitDateRange("1883-04-06/P3M"));
		assertEquals(Arrays.asList(new String[]{"1883-04-01","1883-04-08"}), EventUtility.splitDateRange("1883-04-01/P1W"));
		
		// Recurring interval: July-August 1883-1885
		// Unclear how to use the Rn/ syntax.
		// assertEquals(Arrays.asList(new String[]{"1883-07-01","1883-09-01","1884-07-01","1884-09-01","1885-07-01","1885-09-01"}), EventUtility.splitDateRange("R3/1883-06-01/P2M"));
		
		// Handling for things that don't match the expected pattern for an ISO date range.
		assertEquals(Arrays.asList(new String[]{"1/2/3"}), EventUtility.splitDateRange("1/2/3"));
		assertEquals(Arrays.asList(new String[]{"1880-1890"}), EventUtility.splitDateRange("1880-1890"));
		assertEquals(Arrays.asList(new String[]{"A"}), EventUtility.splitDateRange("A"));
	}

	/**
	 * Test method for {@link org.kurator.validation.utility.EventUtility#eventDateWithinOneYear(java.lang.String)}.
	 */
	@Test
	public void testEventDateWithinOneYear() {
		assertEquals(true, EventUtility.eventDateWithinOneYear("1880"));
		assertEquals(true, EventUtility.eventDateWithinOneYear("0001"));
		assertEquals(true, EventUtility.eventDateWithinOneYear("1880-01"));
		assertEquals(true, EventUtility.eventDateWithinOneYear("1880-01-15"));
		assertEquals(true, EventUtility.eventDateWithinOneYear("2000"));
		assertEquals(true, EventUtility.eventDateWithinOneYear("9999"));
		
		// Ranges within a year
		assertEquals(true, EventUtility.eventDateWithinOneYear("1880-01-15/1880-12-05"));
		assertEquals(true, EventUtility.eventDateWithinOneYear("1880-01-01/1880-12-31"));
		assertEquals(true, EventUtility.eventDateWithinOneYear("1880-01-01/P3D"));
		assertEquals(true, EventUtility.eventDateWithinOneYear("1880-01-01/P3M"));
		
	    // Day which doesn't exist
		assertEquals(false, EventUtility.eventDateWithinOneYear("1880-02-30"));
		assertEquals(false, EventUtility.eventDateWithinOneYear("1700-04-31"));
		
		// Example dates (rfc 3339 and DwC
		assertEquals(true,EventUtility.eventDateWithinOneYear("1985-04-12T23:20:50.52Z"));
		assertEquals(true,EventUtility.eventDateWithinOneYear("1963-03-08T14:07-0600"));
		assertEquals(true,EventUtility.eventDateWithinOneYear("2007-11-13/15"));
		
		// Year 0 valid ISO year.
		assertEquals(true, EventUtility.eventDateWithinOneYear("0000"));
		
		// Ranges that span more than one year
		assertEquals(false, EventUtility.eventDateWithinOneYear("1880/1881"));
		assertEquals(false, EventUtility.eventDateWithinOneYear("1880-12-30/1881-01-02"));  // spans more than one year
		assertEquals(false, EventUtility.eventDateWithinOneYear("1880-02-15/1890"));
		assertEquals(false, EventUtility.eventDateWithinOneYear("1880/1881-01-01"));
		assertEquals(false, EventUtility.eventDateWithinOneYear("1880-12-01/P3M"));
		assertEquals(false, EventUtility.eventDateWithinOneYear("1880-12-31/P3D"));
		
		// not valid dates
		assertEquals(false, EventUtility.eventDateWithinOneYear("0000-00"));
		assertEquals(false, EventUtility.eventDateWithinOneYear("0000-00-00"));
		assertEquals(false, EventUtility.eventDateWithinOneYear("9999-99"));
		assertEquals(false, EventUtility.eventDateWithinOneYear("9999-99-99"));
		assertEquals(false,EventUtility.eventDateWithinOneYear(" "));
		assertEquals(false,EventUtility.eventDateWithinOneYear(""));
		assertEquals(false,EventUtility.eventDateWithinOneYear(null));
		assertEquals(false,EventUtility.eventDateWithinOneYear("\t"));
		assertEquals(false,EventUtility.eventDateWithinOneYear("\n"));
	}

	/**
	 * Test method for {@link org.kurator.validation.utility.EventUtility#eventDateStandardFormat(java.lang.String)}.
	 */
	@Test
	public void testEventDateStandardFormat() {
		assertEquals(true,EventUtility.eventDateStandardFormat("0001"));
		assertEquals(true,EventUtility.eventDateStandardFormat("9999"));
		assertEquals(true,EventUtility.eventDateStandardFormat("1880"));
		assertEquals(true,EventUtility.eventDateStandardFormat("1880-04"));
		assertEquals(true,EventUtility.eventDateStandardFormat("1880-04-02"));
		assertEquals(true,EventUtility.eventDateStandardFormat("1880/1881"));
		assertEquals(true,EventUtility.eventDateStandardFormat("1880-04/1881"));
		assertEquals(true,EventUtility.eventDateStandardFormat("1880-04-02/1881"));
		assertEquals(true,EventUtility.eventDateStandardFormat("1880/1881-02"));
		assertEquals(true,EventUtility.eventDateStandardFormat("1880-04/1881-02"));
		assertEquals(true,EventUtility.eventDateStandardFormat("1880-04-02/1881-02"));
		assertEquals(true,EventUtility.eventDateStandardFormat("1880/1881-02-15"));
		assertEquals(true,EventUtility.eventDateStandardFormat("1880-04/1881-02-15"));
		assertEquals(true,EventUtility.eventDateStandardFormat("1880-04-02/1881-02-15"));
		assertEquals(true,EventUtility.eventDateStandardFormat("9999-99"));
		assertEquals(true,EventUtility.eventDateStandardFormat("9999-99-99"));
		
		// Examples from RFC 3339
		assertEquals(true,EventUtility.eventDateStandardFormat("1985-04-12T23:20:50.52Z"));
		assertEquals(true,EventUtility.eventDateStandardFormat("1996-12-19T16:39:57-08:00"));
		assertEquals(true,EventUtility.eventDateStandardFormat("1990-12-31T23:59:60Z"));
		assertEquals(true,EventUtility.eventDateStandardFormat("1990-12-31T15:59:60-08:00"));
		assertEquals(true,EventUtility.eventDateStandardFormat("1937-01-01T12:00:27.87+00:20"));
		
		// RFC 3339, note in 5.6 that T and Z may be in lower case
		assertEquals(true,EventUtility.eventDateStandardFormat("1990-12-31t23:59:60z"));
		// RFC 3339, note in 5.6 that " " may be used in place of "T" for readability.
		assertEquals(true,EventUtility.eventDateStandardFormat("1990-12-31 23:59:60Z"));
		
		// Examples from dwc:eventDate
		assertEquals(true,EventUtility.eventDateStandardFormat("1963-03-08T14:07-0600"));
		assertEquals(true,EventUtility.eventDateStandardFormat("2009-02-20T08:40Z"));
		assertEquals(true,EventUtility.eventDateStandardFormat("1809-02-12"));
		assertEquals(true,EventUtility.eventDateStandardFormat("1906-06"));
		assertEquals(true,EventUtility.eventDateStandardFormat("1971"));
		assertEquals(true,EventUtility.eventDateStandardFormat("2007-03-01T13:00:00Z/2008-05-11T15:30:00Z"));
		assertEquals(true,EventUtility.eventDateStandardFormat("2007-11-13/15"));   // for second half of period, leading elements that are the same can be ommitted.
		assertEquals(true,EventUtility.eventDateStandardFormat("2007-11-13/12-15")); 
		assertEquals(true,EventUtility.eventDateStandardFormat("2007-11/12")); 
		
		assertEquals(true,EventUtility.eventDateStandardFormat("2007-11-13/P2D"));  // start day and period
		assertEquals(true,EventUtility.eventDateStandardFormat("2007-11-13/P2M"));  // start day and period
		assertEquals(true,EventUtility.eventDateStandardFormat("2007-11-13/P0000-00-02"));  // start day and period
		assertEquals(true,EventUtility.eventDateStandardFormat("2007-03-13/P0000-02-00"));  // start day and period
		
		// Recurring date range
		assertEquals(true,EventUtility.eventDateStandardFormat("2007-11-13/R3P2D"));  // start day and period
		
		assertEquals(false,EventUtility.eventDateStandardFormat("1881/1880"));   // Start before end in interval.
		assertEquals(false,EventUtility.eventDateStandardFormat("1880-1880"));
		
		assertEquals(false,EventUtility.eventDateStandardFormat("1/2"));
		assertEquals(false,EventUtility.eventDateStandardFormat("1"));
		assertEquals(false,EventUtility.eventDateStandardFormat("****-**-**"));  // * for unknown values
		assertEquals(false,EventUtility.eventDateStandardFormat("****/**/**"));
		assertEquals(false,EventUtility.eventDateStandardFormat("1925/**/**"));
		assertEquals(false,EventUtility.eventDateStandardFormat("1925-**-**"));
		assertEquals(false,EventUtility.eventDateStandardFormat("1925-00-00"));
		assertEquals(false,EventUtility.eventDateStandardFormat("1925----"));   // - for unknown values.
	}

	/**
	 * Test method for {@link org.kurator.validation.utility.EventUtility#eventDateExists(java.lang.String)}.
	 */
	@Test
	public void testEventDateExists() {
		assertEquals(true,EventUtility.eventDateExists("1758"));
		assertEquals(true,EventUtility.eventDateExists("0000"));   // Valid ISO 8601 year.  No year 0 in Julian or Gregorian calendars.
		assertEquals(true,EventUtility.eventDateExists("0001"));
		assertEquals(true,EventUtility.eventDateExists("2000"));
		assertEquals(true,EventUtility.eventDateExists("2100"));
		assertEquals(true,EventUtility.eventDateExists("9999"));
		assertEquals(true,EventUtility.eventDateExists("1758-01"));
		assertEquals(true,EventUtility.eventDateExists("1758-01-01"));
		assertEquals(true,EventUtility.eventDateExists("1758-12-31"));
		assertEquals(true,EventUtility.eventDateExists("2016-02-29"));
		assertEquals(true,EventUtility.eventDateExists("2016-02-28/2016-02-29"));
		assertEquals(true,EventUtility.eventDateExists("2015-02-28/2016-02-29"));
		assertEquals(true,EventUtility.eventDateExists("2012-02-29/2016-02-29"));
		assertEquals(true,EventUtility.eventDateExists("2009-02-20T08:40Z"));
		assertEquals(true,EventUtility.eventDateExists("2000-02-29"));
		assertEquals(true,EventUtility.eventDateExists("1880-01-01/P3D"));
		assertEquals(true,EventUtility.eventDateExists("2007-11-13/15"));
		assertEquals(true,EventUtility.eventDateExists("2007-11-13/12-15"));
		assertEquals(true,EventUtility.eventDateExists("2007-11/12"));
		
		assertEquals(false,EventUtility.eventDateExists("1980-02-31"));
		assertEquals(false,EventUtility.eventDateExists("2015-02-29"));
		assertEquals(false,EventUtility.eventDateExists("1700-02-29"));
		assertEquals(false,EventUtility.eventDateExists("1800-02-29"));
		assertEquals(false,EventUtility.eventDateExists("1900-02-29"));
		assertEquals(false,EventUtility.eventDateExists("2015-02-28/2015-02-29"));
		assertEquals(false,EventUtility.eventDateExists("1980-02-30"));
		assertEquals(false,EventUtility.eventDateExists("1980-15-01"));
		assertEquals(false,EventUtility.eventDateExists("1980-01-34"));
		assertEquals(false,EventUtility.eventDateExists("1980-99-99"));
		assertEquals(false,EventUtility.eventDateExists("1980-03-99"));
		assertEquals(false,EventUtility.eventDateExists("1980-01-34/1980-01-35"));
		assertEquals(false,EventUtility.eventDateExists("1980-01-01/1980-01-35"));
		assertEquals(false,EventUtility.eventDateExists("1980-01-34/1980-01-01"));
		
		assertEquals(false,EventUtility.eventDateExists("2009-02-20T25:40Z"));
		assertEquals(false,EventUtility.eventDateExists("2009-02-20T02:99Z"));
		
		assertEquals(false,EventUtility.eventDateExists("9999-99"));
		assertEquals(false,EventUtility.eventDateExists("9999-99-99"));
		assertEquals(false,EventUtility.eventDateExists("0000-00"));
		assertEquals(false,EventUtility.eventDateExists("0000-00-00"));
	}

	/**
	 * Test method for {@link org.kurator.validation.utility.EventUtility#eventInternallyConsistent(java.lang.String, java.lang.Integer, java.lang.Integer, java.lang.Integer, java.lang.Integer, java.lang.Integer)}.
	 */
	@Test
	public void testEventInternallyConsistent() {
//		fail("Not yet implemented");
	}

	/**
	 * Test method for {@link org.kurator.validation.utility.EventUtility#eventDateVerbatimDateConsistent(java.lang.String, java.lang.Integer, java.lang.Integer, java.lang.Integer, java.lang.Integer, java.lang.Integer)}.
	 */
	@Test
	public void testEventDateVerbatimDateConsistent() {
//		fail("Not yet implemented");
	}

	/**
	 * Test method for {@link org.kurator.validation.utility.EventUtility#assembleEventDate(java.lang.Integer, java.lang.Integer, java.lang.Integer, java.lang.Integer, java.lang.Integer)}.
	 */
	@Test
	public void testAssembleEventDate() {
//		fail("Not yet implemented");
	}

}
