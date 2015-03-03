package org.kurator.validation.exceptions;

import org.kurator.akka.data.SpacedStringBuilder;

@SuppressWarnings("serial")
public class MissingFieldException extends ValidationException {

	public final String fieldName;

	public MissingFieldException(String componentName, String fieldName, String condition) {
		super(buildMessage(componentName, fieldName, condition));
		this.fieldName = fieldName;
	}

	public MissingFieldException(String componentName, String fieldName) {
		this(componentName, fieldName, null);
	}

	private static String buildMessage(String componentName, String fieldName, String condition) {
		return new SpacedStringBuilder()
			.append(componentName)
			.append("requires value for")
			.append(fieldName)
			.append(condition)
			.toString();
	}
}
