import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

const CRIME_TYPE_LABELS: Record<string, string> = {
  THEFT: "Theft",
  BATTERY: "Battery / Assault",
  CRIMINAL_DAMAGE: "Criminal Damage / Vandalism",
  NARCOTICS: "Drug Offenses",
  BURGLARY: "Burglary",
  MOTOR_VEHICLE_THEFT: "Motor Vehicle Theft",
  ROBBERY: "Robbery",
  DECEPTIVE_PRACTICE: "Fraud / Forgery",
  ASSAULT: "Aggravated Assault",
  WEAPONS_VIOLATION: "Weapons Violation",
  PUBLIC_PEACE_VIOLATION: "Disorderly Conduct",
  OFFENSE_INVOLVING_CHILDREN: "Offenses Involving Children",
  OTHER_OFFENSE: "Other Offense",
  INTERFERENCE_WITH_PUBLIC_OFFICER: "Obstruction / Resisting Arrest",
  LIQUOR_LAW_VIOLATION: "Liquor Law Violation",
  PROSTITUTION: "Prostitution / Solicitation",
  CRIMINAL_TRESPASS: "Criminal Trespassing",
  STALKING: "Stalking / Harassment",
  SEX_OFFENSE: "Sex Offense",
  KIDNAPPING: "Kidnapping / Abduction",
  ARSON: "Arson",
  HOMICIDE: "Homicide / Manslaughter",
  HUMAN_TRAFFICKING: "Human Trafficking",
  INTIMIDATION: "Intimidation / Threats",
  NON_CRIMINAL: "Non-Criminal Incident",
  CONCEALED_CARRY_LICENSE_VIOLATION: "Concealed Carry Violation",
};

export function formatCrimeType(code: string): string {
  return CRIME_TYPE_LABELS[code.toUpperCase()] ?? titleCase(code);
}

export function titleCase(s: string): string {
  return s
    .toLowerCase()
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
