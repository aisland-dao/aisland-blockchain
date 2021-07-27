#![cfg_attr(not(feature = "std"), no_std)]

use core::str;
use core::str::FromStr;
/// Module to manage the function for the MarketPlace
use frame_support::{
    decl_error, decl_event, decl_module, decl_storage, dispatch, ensure, traits::Currency,
};
use frame_system::{ensure_root, ensure_signed};
use sp_std::prelude::*;


#[cfg(test)]
mod mock;

#[cfg(test)]
mod tests;

/// Module configuration
pub trait Config: frame_system::Config {
    //pub trait Config: frame_system::Config + Sized {
    type Event: From<Event<Self>> + Into<<Self as frame_system::Config>::Event>;
    type Currency: Currency<Self::AccountId>;
}
pub type Balance = u128;

// The runtime storage items
decl_storage! {
    trait Store for Module<T: Config> as marketplace {
        // we use a safe crypto hashing by blake2_128
        // Seller data storage
        Sellers get(fn get_seller): map hasher(blake2_128_concat) T::AccountId => Option<Vec<u8>>;
        // Product Departments
        ProductDepartments get(fn get_products_department): map hasher(blake2_128_concat) u32 => Option<Vec<u8>>;
        // Product Categories
        ProductCategories get(fn get_products_category): double_map hasher(blake2_128_concat) u32,hasher(blake2_128_concat) u32 => Option<Vec<u8>>;
        // Standard Iso country code and official name
        IsoCountries get(fn get_iso_country): map hasher(blake2_128_concat) Vec<u8> => Option<Vec<u8>>;
        // Standard Iso dial code for country code
        IsoDialcode get(fn get_iso_dialcode): map hasher(blake2_128_concat) Vec<u8> => Option<Vec<u8>>;
    }
}

// We generate events to inform the users of succesfully actions.
decl_event!(
    pub enum Event<T>
    where
        AccountId = <T as frame_system::Config>::AccountId,
    {
        MarketPlaceDepartmentCreated(u32, Vec<u8>),         // New department created
        MarketPlaceDepartmentDestroyed(u32),                // Department has been destroyed/removed
        MarketPlaceSellerCreated(AccountId, Vec<u8>),       // New seller has been created
        MarketPlaceSellerDestroyed(AccountId),              // Seller destroyed
        MarketPlaceCategoryCreated(u32, u32, Vec<u8>),      // New producct category has been created
        MarketPlaceCategoryDestroyed(u32, u32),             // Product category has been destroyed
        MarketPlaceIsoCountryCreated(Vec<u8>, Vec<u8>),     // New Iso contry code has been created
        MarketPlaceIsoCountryDestroyed(Vec<u8>),            // Iso contry code has been destroyed
        MarketPlaceIsoDialCodeCreated(Vec<u8>, Vec<u8>),    // New country dial code has been created
        MarketPlaceIsoDialCodeDestroyed(Vec<u8>),           // A country dial code has been destroyed
    }
);

// Errors to inform users that something went wrong.
decl_error! {
    pub enum Error for Module<T: Config> {
        /// Uid cannot be zero
        UidCannotBeZero,
        /// Configuration data is too short
        ConfigurationTooShort,
        /// Configuration data is too long
        ConfigurationTooLong,
        /// Seller is already present
        SellerAlreadyPresent,
        /// Invalid json sintax
        InvalidJson,
        /// Department Description is too short, it should be > 3 bytes
        DepartmentDescriptionTooShort,
        // Department Description is too long, it should be < 128 bytes
        DepartmentDescriptionTooLong,
        /// Department Id cannot be equale to zero
        DepartmentUidCannotBeZero,
        /// Department is already present on chain
        DepartmentAlreadyPresent,
        /// Department not found on chain
        DepartmentNotFound,
        /// Category ID cannot be equal to zero
        CategoryUidCannotBeZero,
        /// Category Description is too short
        CategoryDescriptionTooShort,
        /// Category Description is too long
        CategoryDescriptionTooLong,
        /// Category has not been found
        CategoryNotFound,
        /// Product category is already present on chain
        ProductCategoryAlreadyPresent,
        /// Product category not found on chain
        ProductCategoryNotFound,
        /// The country code is wrong, it must be long 2 bytes
        WrongLengthCountryCode,
        /// The country name is too short, it must be >=3
        CountryNameTooShort,
        /// Country code already present on chain
        CountryCodeAlreadyPresent,
        /// Country code not found on chain
        CountryCodeNotFound,
        /// International Dial code is too short it must be at the least 2 bytes
        DialcodeTooShort,
        /// Seller type can be 1 for Company, 2 for Professional, 3 for Private
        SellerTypeInvalid,
        /// Seller name is too short, it must be at least 5 bytes
        SellerNameTooShort,
        /// The Sellet city is too short, it mut be at the least 5 bytes
        SellerCityTooShort,
        /// The seller address is too long, maximum 128 bytes
        SellerAddressTooLong,
        /// The seller zip code is too long, maximum 12 bytes
        SellerZipCodeTooLong,
        /// Po Box is too long, maximum 64 bytes
        SellerPoBoxTooLong,
        /// Seller certification description is too short, must be > 3 bytes
        SellerCertificationDescriptionTooShort,
        /// Seller certification description is too long, must be <= 64 bytes
        SellerCertificationDescriptionTooLong,
        /// Seller certificate verification is too short
        SellerCertificateVerificationTooShort,
        /// Seller certificate verification is too long
        SellerCertificateVerificationTooLong,
        /// Seller info email is wrong
        SellerInfoEmailIsWrong,
        /// Seller support email is wrong
        SellerSupportEmailIsWrong,
        /// Phone description is too short, it should be at the least 4 bytes
        SellerPhoneDescriptionTooShort,
        /// Phone description is too long, maximum 64 bytes
        SellerPhoneDescriptionTooLong,
        /// Phone number is too short at the least > 3 bytes
        SellerPhoneNumberTooShort,
        /// Phone number is too long, maximum 21 bytes
        SellerPhoneNumberTooLong,
        /// Categories of product/service sold from seller is missing
        SellerCategoriesMissing,
        /// Included countries for shipment are missing at the least "countries":[], should be set
        SellercountriesMissing,
        /// the inout fiels is not set for the the country, it should be 0 for included, 1 for excluded country with default worldwide
        IncludedExcludedCountryValueIsMissing,
        /// The latitude of the center point for the shipment area, is missing
        ShipmentAreaCenterLatitudeIsMissing,
        /// The longitude of the center point for the shipment area, is missing
        ShipmentAreaCenterLongitudeIsMissing,
        /// The latitude of the border point for the shipment area, is missing
        ShipmentAreaBorderLatitudeIsMissing,
        /// The longitude of the border point for the shipment area, is missing
        ShipmentAreaBorderLongituteIsMissing,
        /// Seller Social Url is wrong
        SellerSocialUrlIsWrong,
        /// Seller web site is wrong
        SellerWebsiteUrlIsWrong,
        /// Seller the url for certificate verification is wrong
        SellerCertificationUrlIsWrong,
        /// Seller phone number is wrong
        SellerPhoneNumberIsWrong,
        /// Seller data has not been found on chain
        SellerDataNotFound,
    }
}

// Dispatchable functions allows users to interact with the pallet and invoke state changes.
decl_module! {
    pub struct Module<T: Config> for enum Call where origin: T::Origin {
        // Errors must be initialized
        type Error = Error<T>;
        // Events must be initialized
        fn deposit_event() = default;

        /// Create a new product department
        #[weight = 1000]
        pub fn create_product_department(origin, uid: u32, description: Vec<u8>) -> dispatch::DispatchResult {
            // check the request is signed from root
            let _sender = ensure_root(origin)?;
            // check uid >0
            ensure!(uid > 0, Error::<T>::DepartmentUidCannotBeZero);
            //check description length
            ensure!(description.len() > 3, Error::<T>::DepartmentDescriptionTooShort);
            ensure!(description.len() < 128, Error::<T>::DepartmentDescriptionTooLong);
            // check the department is not alreay present on chain
            ensure!(ProductDepartments::contains_key(uid)==false, Error::<T>::DepartmentAlreadyPresent);
            // store the department
            ProductDepartments::insert(uid,description.clone());
            // Generate event
            Self::deposit_event(RawEvent::MarketPlaceDepartmentCreated(uid,description));
            // Return a successful DispatchResult
            Ok(())
        }
        /// Destroy a product department
        #[weight = 1000]
        pub fn destroy_product_department(origin, uid: u32) -> dispatch::DispatchResult {
            // check the request is signed from Super User
            let _sender = ensure_root(origin)?;
            // verify the department exists
            ensure!(ProductDepartments::contains_key(&uid)==true, Error::<T>::DepartmentNotFound);
            // Remove department
            ProductDepartments::take(uid);
            // Generate event
            //it can leave orphans, anyway it's a decision of the super user
            Self::deposit_event(RawEvent::MarketPlaceDepartmentDestroyed(uid));
            // Return a successful DispatchResult
            Ok(())
        }
        /// Create a new product category
        #[weight = 1000]
        pub fn create_product_category(origin, uiddepartment: u32, uidcategory: u32, description: Vec<u8>) -> dispatch::DispatchResult {
            // check the request is signed from the Super User
            let _sender = ensure_root(origin)?;
            // check uid department >0
            ensure!(uiddepartment > 0, Error::<T>::DepartmentUidCannotBeZero);
            // check uid category >0
            ensure!(uidcategory > 0, Error::<T>::CategoryUidCannotBeZero);
            //check description length
            ensure!(description.len() > 3, Error::<T>::CategoryDescriptionTooShort);
            ensure!(description.len() < 128, Error::<T>::CategoryDescriptionTooLong);
            // check the department is  alreay present on chain
            ensure!(ProductDepartments::contains_key(uiddepartment)==true, Error::<T>::DepartmentNotFound);
            // check the department/category is not alreay present on chain
            ensure!(ProductCategories::contains_key(uiddepartment,uidcategory)==false, Error::<T>::ProductCategoryAlreadyPresent);
            // store the department
            ProductCategories::insert(uiddepartment,uidcategory,description.clone());
            // Generate event
            Self::deposit_event(RawEvent::MarketPlaceCategoryCreated(uiddepartment,uidcategory,description));
            // Return a successful DispatchResult
            Ok(())
        }
        /// Destroy a product category
        #[weight = 1000]
        pub fn destroy_product_category(origin, uiddepartment: u32, uidcategory: u32) -> dispatch::DispatchResult {
            // check the request is signed from the Super User
            let _sender = ensure_root(origin)?;
            // verify the department/category exists
            ensure!(ProductCategories::contains_key(&uiddepartment,&uidcategory)==true, Error::<T>::ProductCategoryNotFound);
            // Remove department
            ProductCategories::take(uiddepartment,uidcategory);
            // Generate event
            //it can leave orphans, anyway it's a decision of the super user
            Self::deposit_event(RawEvent::MarketPlaceCategoryDestroyed(uiddepartment, uidcategory));
            // Return a successful DispatchResult
            Ok(())
        }
        /// Create a new seller
        #[weight = 10000]
        pub fn create_update_seller(origin, configuration: Vec<u8>) -> dispatch::DispatchResult {
            // check the request is signed
            let sender = ensure_signed(origin)?;
            //check configuration length
            ensure!(configuration.len() > 12, Error::<T>::ConfigurationTooShort);
            ensure!(configuration.len() < 8192, Error::<T>::ConfigurationTooLong);
            // check json validity
            ensure!(json_check_validity(configuration.clone()),Error::<T>::InvalidJson);
            // checking seller type
            let sellertype=json_get_value(configuration.clone(),"sellertype".as_bytes().to_vec());
            let sellertypeu32=vec_to_u32(sellertype);
            ensure!(sellertypeu32==1 || sellertypeu32==2 || sellertypeu32==3 ,Error::<T>::SellerTypeInvalid);
            // checking company name or name/surname
            let sellername=json_get_value(configuration.clone(),"name".as_bytes().to_vec());
            ensure!(sellername.len()>5,Error::<T>::SellerNameTooShort);
            // address we check for maximum lenght of 128 bytes
            let selleraddress=json_get_value(configuration.clone(),"address".as_bytes().to_vec());
            ensure!(selleraddress.len()<128,Error::<T>::SellerAddressTooLong);
            // zip code we check for maximum lenght of 12 bytes
            let sellerzip=json_get_value(configuration.clone(),"zip".as_bytes().to_vec());
            ensure!(sellerzip.len()<13,Error::<T>::SellerZipCodeTooLong);
            // checking the city minimum 3 bytes
            let sellerpobox=json_get_value(configuration.clone(),"pobox".as_bytes().to_vec());
            ensure!(sellerpobox.len()<64,Error::<T>::SellerPoBoxTooLong);
            // checking the city minimum 3 bytes
            let sellercity=json_get_value(configuration.clone(),"city".as_bytes().to_vec());
            ensure!(sellercity.len()>5,Error::<T>::SellerCityTooShort);
            // checking websites
            let websites=json_get_value(configuration.clone(),"websites".as_bytes().to_vec());
            if websites.len()>0 {
                let mut x=0;
                loop {  
                    let w=json_get_recordvalue(websites.clone(),x);
                    if w.len()==0 {
                        break;
                    }
                    let weburl=json_get_value(w.clone(),"weburl".as_bytes().to_vec());
                    ensure!(aisland_validate_weburl(weburl)==true,Error::<T>::SellerWebsiteUrlIsWrong);
                    x=x+1;
                }
            }
            // checking social url
            let socialurls=json_get_value(configuration.clone(),"socialurls".as_bytes().to_vec());
            if socialurls.len()>0 {
                let mut x=0;
                loop {  
                    let w=json_get_recordvalue(socialurls.clone(),x);
                    if w.len()==0 {
                        break;
                    }
                    let socialurl=json_get_value(w.clone(),"socialurl".as_bytes().to_vec());
                    ensure!(aisland_validate_weburl(socialurl)==true,Error::<T>::SellerSocialUrlIsWrong);
                    x=x+1;
                }
            }
            // checking certifications
            let certifications=json_get_value(configuration.clone(),"certifications".as_bytes().to_vec());
            if certifications.len()>0 {
                let mut x=0;
                loop {  
                    let w=json_get_recordvalue(certifications.clone(),x);
                    if w.len()==0 {
                        break;
                    }
                    let certificationdescription=json_get_value(configuration.clone(),"description".as_bytes().to_vec());
                    let certificateverificationurl=json_get_value(configuration.clone(),"verificationurl".as_bytes().to_vec());
                    ensure!(certificationdescription.len()>3,Error::<T>::SellerCertificationDescriptionTooShort);
                    ensure!(certificationdescription.len()<=64,Error::<T>::SellerCertificationDescriptionTooLong);
                    ensure!(certificateverificationurl.len()>3,Error::<T>::SellerCertificateVerificationTooShort);
                    ensure!(certificateverificationurl.len()<=64,Error::<T>::SellerCertificateVerificationTooLong);
                    ensure!(aisland_validate_weburl(certificateverificationurl.clone())==true,Error::<T>::SellerCertificationUrlIsWrong);
                    x=x+1;
                }
            }
            // checking emailinfo
            let emailinfo=json_get_value(configuration.clone(),"emailinfo".as_bytes().to_vec());
            ensure!(emailinfo.len()>5,Error::<T>::SellerInfoEmailIsWrong);
            ensure!(aisland_validate_email(emailinfo.clone()),Error::<T>::SellerInfoEmailIsWrong);
            // checking email support
            let emailsupport=json_get_value(configuration.clone(),"emailsupport".as_bytes().to_vec());
            ensure!(emailsupport.len()>5,Error::<T>::SellerSupportEmailIsWrong);
            ensure!(aisland_validate_email(emailsupport.clone()),Error::<T>::SellerSupportEmailIsWrong);

            // checking phone numbers
            let phones=json_get_value(configuration.clone(),"phones".as_bytes().to_vec());
            if phones.len()>0 {
                let mut x=0;
                loop {  
                    let w=json_get_recordvalue(phones.clone(),x);
                    if w.len()==0 {
                        break;
                    }
                    let phonedescription=json_get_value(configuration.clone(),"phonedescription".as_bytes().to_vec());
                    let phonenumber=json_get_value(configuration.clone(),"phonebumber".as_bytes().to_vec());
                    ensure!(phonedescription.len()>3,Error::<T>::SellerPhoneDescriptionTooShort);
                    ensure!(phonedescription.len()<=64,Error::<T>::SellerPhoneDescriptionTooLong);
                    ensure!(phonenumber.len()>3,Error::<T>::SellerPhoneNumberTooShort);
                    ensure!(phonenumber.len()<=23,Error::<T>::SellerPhoneNumberTooLong);
                    ensure!(aisland_validate_phonenumber(phonenumber)==true,Error::<T>::SellerPhoneNumberIsWrong);
                    x=x+1;
                }
            }
            // checking categories of products/services with the department
            let categories=json_get_value(configuration.clone(),"categories".as_bytes().to_vec());
            ensure!(categories.len()>0,Error::<T>::SellerCategoriesMissing);
            let mut x=0;
            let mut nc=0;
            loop {  
                let c=json_get_recordvalue(categories.clone(),x);
                if c.len()==0 {
                    break;
                }
                let category=json_get_value(configuration.clone(),"category".as_bytes().to_vec());
                let department=json_get_value(configuration.clone(),"department".as_bytes().to_vec());
                let categoryu32=vec_to_u32(category);
                let departmentu32=vec_to_u32(department);
                ensure!(ProductCategories::contains_key(categoryu32,departmentu32)==true, Error::<T>::ProductCategoryNotFound);
                x=x+1;
                nc=nc+1;
            }
            // check that we have at least one valid product category
            ensure!(nc>0,Error::<T>::SellerCategoriesMissing);
            // checking included countries of shipment, if not set means worldwide less the excluded countries
            let countries=json_get_value(configuration.clone(),"countries".as_bytes().to_vec());
            ensure!(countries.len()>0,Error::<T>::SellercountriesMissing);
            let mut x=0;
            loop {  
                let c=json_get_recordvalue(countries.clone(),x);
                if c.len()==0 {
                    break;
                }
                let country=json_get_value(configuration.clone(),"country".as_bytes().to_vec());
                let inout=json_get_value(configuration.clone(),"inout".as_bytes().to_vec());
                let inoutv=vec_to_u32(inout);
                ensure!(IsoCountries::contains_key(country)==true, Error::<T>::CountryCodeNotFound);
                ensure!(inoutv==0 || inoutv==1,Error::<T>::IncludedExcludedCountryValueIsMissing);
                x=x+1;
            }
            // check that we have at least one valid product category
            ensure!(nc>0,Error::<T>::SellerCategoriesMissing);
            // delivery area can be delimited by GPS coordinates where a first point is the center of a circle and second point is the border of the same circle
            // this is useful if a service/product can be delivered only around a certain place
            let shipmentarea=json_get_value(configuration.clone(),"shipmentarea".as_bytes().to_vec());
            if shipmentarea.len()>0{
                let centerlatitude=json_get_value(shipmentarea.clone(),"centerlatitude".as_bytes().to_vec());
                let centerlongitude=json_get_value(shipmentarea.clone(),"centerlongitude".as_bytes().to_vec());
                let borderlatitude=json_get_value(shipmentarea.clone(),"borderlatitude".as_bytes().to_vec());
                let borderlongitude=json_get_value(shipmentarea.clone(),"borderlongitude".as_bytes().to_vec());
                ensure!(centerlatitude.len()>0,Error::<T>::ShipmentAreaCenterLatitudeIsMissing);
                ensure!(centerlongitude.len()>0,Error::<T>::ShipmentAreaCenterLongitudeIsMissing);
                ensure!(borderlatitude.len()>0,Error::<T>::ShipmentAreaBorderLatitudeIsMissing);
                ensure!(borderlongitude.len()>0,Error::<T>::ShipmentAreaBorderLongituteIsMissing);
            }
            if Sellers::<T>::contains_key(&sender)==false {
                // Insert new seller
                Sellers::<T>::insert(sender.clone(),configuration.clone());
            } else {
                // Replace Seller Data 
                Sellers::<T>::take(sender.clone());
                Sellers::<T>::insert(sender.clone(),configuration.clone());
            }
            // Generate event
            Self::deposit_event(RawEvent::MarketPlaceSellerCreated(sender,configuration));
            // Return a successful DispatchResult
            Ok(())
        }
        /// Destroy a Seller
        #[weight = 1000]
        pub fn destroy_seller(origin) -> dispatch::DispatchResult {
            // check the request is signed
            let sender = ensure_signed(origin)?;
            // verify the seller exists
            ensure!(Sellers::<T>::contains_key(&sender)==true, Error::<T>::SellerDataNotFound);
            // Remove Seller
            Sellers::<T>::take(sender.clone());
            // Generate event
            //it can leave orphans, anyway it's a decision of the super user
            Self::deposit_event(RawEvent::MarketPlaceSellerDestroyed(sender));
            // Return a successful DispatchResult
            Ok(())
        }
        /// Create a new Iso country code and name
        #[weight = 1000]
        pub fn create_iso_country(origin, countrycode: Vec<u8>, countryname: Vec<u8>) -> dispatch::DispatchResult {
            // check the request is signed from the Super User
            let _sender = ensure_root(origin)?;
            // check country code length == 2
            ensure!(countrycode.len()==2, Error::<T>::WrongLengthCountryCode);
            // check country name length  >= 3
            ensure!(countryname.len()>=3, Error::<T>::CountryNameTooShort);
            // check the country is not alreay present on chain
            ensure!(IsoCountries::contains_key(&countrycode)==false, Error::<T>::CountryCodeAlreadyPresent);
            // store the Iso Country Code and Name
            IsoCountries::insert(countrycode.clone(),countryname.clone());
            // Generate event
            Self::deposit_event(RawEvent::MarketPlaceIsoCountryCreated(countrycode,countryname));
            // Return a successful DispatchResult
            Ok(())
        }
        /// Destroy an Iso country code and name
        #[weight = 1000]
        pub fn destroy_iso_country(origin, countrycode: Vec<u8>,) -> dispatch::DispatchResult {
            // check the request is signed from the Super User
            let _sender = ensure_root(origin)?;
            // verify the country code exists
            ensure!(IsoCountries::contains_key(&countrycode)==true, Error::<T>::CountryCodeNotFound);
            // Remove country code
            IsoCountries::take(countrycode.clone());
            // Generate event
            //it can leave orphans, anyway it's a decision of the super user
            Self::deposit_event(RawEvent::MarketPlaceIsoCountryDestroyed(countrycode));
            // Return a successful DispatchResult
            Ok(())
        }
         /// Create a new Iso country code and name
         #[weight = 1000]
         pub fn create_dialcode_country(origin, countrycode: Vec<u8>, dialcode: Vec<u8>) -> dispatch::DispatchResult {
             // check the request is signed from the Super User
             let _sender = ensure_root(origin)?;
             // check country code length == 2
             ensure!(countrycode.len()==2, Error::<T>::WrongLengthCountryCode);
             // check country name length  >= 3
             ensure!(dialcode.len()>=2, Error::<T>::DialcodeTooShort);
             // check the dialcode is not alreay present on chain
             ensure!(IsoDialcode::contains_key(&countrycode)==false, Error::<T>::CountryCodeAlreadyPresent);
             // store the Iso Dial Code
             IsoDialcode::insert(countrycode.clone(),dialcode.clone());
             // Generate event
             Self::deposit_event(RawEvent::MarketPlaceIsoDialCodeCreated(countrycode,dialcode));
             // Return a successful DispatchResult
             Ok(())
         }
         /// Destroy an Iso country code and name
         #[weight = 1000]
         pub fn destroy_dialcode_country(origin, countrycode: Vec<u8>,) -> dispatch::DispatchResult {
             // check the request is signed from the Super User
             let _sender = ensure_root(origin)?;
             // verify the country code exists
             ensure!(IsoDialcode::contains_key(&countrycode)==true, Error::<T>::CountryCodeNotFound);
             // Remove country code
             IsoDialcode::take(countrycode.clone());
             // Generate event
             //it can leave orphans, anyway it's a decision of the super user
             Self::deposit_event(RawEvent::MarketPlaceIsoDialCodeDestroyed(countrycode));
             // Return a successful DispatchResult
             Ok(())
         }
    }
}
// function to validate a json string for no/std. It does not allocate of memory
fn json_check_validity(j: Vec<u8>) -> bool {
    // minimum lenght of 2
    if j.len() < 2 {
        return false;
    }
    // checks star/end with {}
    if *j.get(0).unwrap() == b'{' && *j.get(j.len() - 1).unwrap() != b'}' {
        return false;
    }
    // checks start/end with []
    if *j.get(0).unwrap() == b'[' && *j.get(j.len() - 1).unwrap() != b']' {
        return false;
    }
    // check that the start is { or [
    if *j.get(0).unwrap() != b'{' && *j.get(0).unwrap() != b'[' {
        return false;
    }
    //checks that end is } or ]
    if *j.get(j.len() - 1).unwrap() != b'}' && *j.get(j.len() - 1).unwrap() != b']' {
        return false;
    }
    //checks " opening/closing and : as separator between name and values
    let mut s: bool = true;
    let mut d: bool = true;
    let mut pg: bool = true;
    let mut ps: bool = true;
    let mut bp = b' ';
    for b in j {
        if b == b'[' && s {
            ps = false;
        }
        if b == b']' && s && ps == false {
            ps = true;
        } else if b == b']' && s && ps == true {
            ps = false;
        }
        if b == b'{' && s {
            pg = false;
        }
        if b == b'}' && s && pg == false {
            pg = true;
        } else if b == b'}' && s && pg == true {
            pg = false;
        }
        if b == b'"' && s && bp != b'\\' {
            s = false;
            bp = b;
            d = false;
            continue;
        }
        if b == b':' && s {
            d = true;
            bp = b;
            continue;
        }
        if b == b'"' && !s && bp != b'\\' {
            s = true;
            bp = b;
            d = true;
            continue;
        }
        bp = b;
    }
    //fields are not closed properly
    if !s {
        return false;
    }
    //fields are not closed properly
    if !d {
        return false;
    }
    //fields are not closed properly
    if !ps {
        return false;
    }
    // every ok returns true
    return true;
}
// function to get record {} from multirecord json structure [{..},{.. }], it returns an empty Vec when the records is not present
fn json_get_recordvalue(ar: Vec<u8>, p: i32) -> Vec<u8> {
    let mut result = Vec::new();
    let mut op = true;
    let mut cn = 0;
    let mut lb = b' ';
    for b in ar {
        if b == b',' && op == true {
            cn = cn + 1;
            continue;
        }
        if b == b'[' && op == true && lb != b'\\' {
            continue;
        }
        if b == b']' && op == true && lb != b'\\' {
            continue;
        }
        if b == b'{' && op == true && lb != b'\\' {
            op = false;
        }
        if b == b'}' && op == false && lb != b'\\' {
            op = true;
        }
        // field found
        if cn == p {
            result.push(b);
        }
        lb = b.clone();
    }
    return result;
}

// function to get value of a field for Substrate runtime (no std library and no variable allocation)
fn json_get_value(j: Vec<u8>, key: Vec<u8>) -> Vec<u8> {
    let mut result = Vec::new();
    let mut k = Vec::new();
    let keyl = key.len();
    let jl = j.len();
    k.push(b'"');
    for xk in 0..keyl {
        k.push(*key.get(xk).unwrap());
    }
    k.push(b'"');
    k.push(b':');
    let kl = k.len();
    for x in 0..jl {
        let mut m = 0;
        let mut xx = 0;
        if x + kl > jl {
            break;
        }
        for i in x..x + kl {
            if *j.get(i).unwrap() == *k.get(xx).unwrap() {
                m = m + 1;
            }
            xx = xx + 1;
        }
        if m == kl {
            let mut lb = b' ';
            let mut op = true;
            let mut os = true;
            for i in x + kl..jl - 1 {
                if *j.get(i).unwrap() == b'[' && op == true && os == true {
                    os = false;
                }
                if *j.get(i).unwrap() == b'}' && op == true && os == false {
                    os = true;
                }
                if *j.get(i).unwrap() == b':' && op == true {
                    continue;
                }
                if *j.get(i).unwrap() == b'"' && op == true && lb != b'\\' {
                    op = false;
                    continue;
                }
                if *j.get(i).unwrap() == b'"' && op == false && lb != b'\\' {
                    break;
                }
                if *j.get(i).unwrap() == b'}' && op == true {
                    break;
                }
                if *j.get(i).unwrap() == b',' && op == true && os == true {
                    break;
                }
                result.push(j.get(i).unwrap().clone());
                lb = j.get(i).unwrap().clone();
            }
            break;
        }
    }
    return result;
}
//function to convert a vector to u32 with a default value of 0
fn vec_to_u32(v:Vec<u8>) -> u32{
    let v_slice=v.as_slice();
    let v_str=match str::from_utf8(&v_slice){
        Ok(f) => f,
        Err(_) => "0"
    };
    let v_value:u32 = match u32::from_str(v_str){
        Ok(f) => f,
        Err(_) => 0,
    };
    v_value
}
// function to validate and email address, return true/false
fn aisland_validate_email(email:Vec<u8>) -> bool {
    let mut flagat=false;
    let mut valid=false;
    let mut phase=1;
    let mut dotphase2=false;
    for c in email {
        if c==64 {
            flagat=true;
            phase=2;
            continue;
        }
        // check for allowed char in the first part of the email address before @
        if phase==1 {
            if  (c>=65 && c<=90) ||
                (c>=97 && c<=122) ||
                c==45 || c==46 || c==95 {
                    valid=true;
                }else
                {
                    valid=false;
                    break;
                }
        }   
        // check for allowed char in the second part of the email address before @
        if phase==2 {
            if  (c>=65 && c<=90) ||
                (c>=97 && c<=122) ||
                c==45 || c==46 {
                    valid=true;
                }else
                {
                    valid=false;
                    break;
                }
                if c==46 {
                    dotphase2=true;
                }
        }

    }
    // return validity true/false
    if flagat==true && dotphase2==true{
        return valid;
    }else {
        return flagat;
    }   
}
// function to validate an web url return true/false
fn aisland_validate_weburl(weburl:Vec<u8>) -> bool {
    let mut valid=false;
    let mut x=0;
    let mut httpsflag=false;
    let mut httpflag=false;
    let mut startpoint=0;
    let mut https: Vec<u8>= Vec::new();
    https.push(b'h');
    https.push(b't');
    https.push(b't');
    https.push(b'p');
    https.push(b's');
    https.push(b':');
    https.push(b'/');
    https.push(b'/');
    let mut http: Vec<u8>= Vec::new();
    http.push(b'h');
    http.push(b't');
    http.push(b't');
    http.push(b'p');
    http.push(b':');
    http.push(b'/');
    http.push(b'/');
    let mut httpscomp: Vec<u8> =Vec::new();
    httpscomp.push(weburl[0]);
    httpscomp.push(weburl[1]);
    httpscomp.push(weburl[2]);
    httpscomp.push(weburl[3]);
    httpscomp.push(weburl[4]);
    httpscomp.push(weburl[5]);
    httpscomp.push(weburl[6]);
    httpscomp.push(weburl[7]);
    let mut httpcomp: Vec<u8> =Vec::new();
    httpcomp.push(weburl[0]);
    httpcomp.push(weburl[1]);
    httpcomp.push(weburl[2]);
    httpcomp.push(weburl[3]);
    httpcomp.push(weburl[4]);
    httpcomp.push(weburl[5]);
    httpcomp.push(weburl[6]);
    if https==httpscomp {
        httpsflag=true;
    }
    if http==httpcomp {
        httpflag=true;
    }
    if httpflag==false && httpsflag==false {
        return false;
    }
    if httpsflag==true{
        startpoint=8;
    }
    if httpflag==true{
        startpoint=7;
    }
    for c in weburl {    
        if x<startpoint {
            x=x+1;
            continue;
        }
        // check for allowed chars    
        if  (c>=32 && c<=95) ||
            (c>=97 && c<=126) {
            valid=true;
        }else{
            valid=false;
            break;
        }
    }
    return valid;
}
// function to validate a phone number
fn aisland_validate_phonenumber(phonenumber:Vec<u8>) -> bool {
    // check maximum lenght
    if phonenumber.len()>23{
        return false;
    }
    // check admitted bytes
    let mut x=0;
    for v in phonenumber.clone() {
        if (v>=48 && v<=57) || (v==43 && x==0){
            x=x+1;
        }else {
            return false;
        }
    }
    // load international prefixes table
    let mut p: Vec<Vec<u8>> = Vec::new();
    p.push("972".into());
    p.push("93".into());
    p.push("355".into());
    p.push("213".into());
    p.push("376".into());
    p.push("244".into());
    p.push("54".into());
    p.push("374".into());
    p.push("297".into());
    p.push("61".into());
    p.push("43".into());
    p.push("994".into());
    p.push("973".into());
    p.push("880".into());
    p.push("375".into());
    p.push("32".into());
    p.push("501".into());
    p.push("229".into());
    p.push("975".into());
    p.push("387".into());
    p.push("267".into());
    p.push("55".into());
    p.push("246".into());
    p.push("359".into());
    p.push("226".into());
    p.push("257".into());
    p.push("855".into());
    p.push("237".into());
    p.push("1".into());
    p.push("238".into());
    p.push("345".into());
    p.push("236".into());
    p.push("235".into());
    p.push("56".into());
    p.push("86".into());
    p.push("61".into());
    p.push("57".into());
    p.push("269".into());
    p.push("242".into());
    p.push("682".into());
    p.push("506".into());
    p.push("385".into());
    p.push("53".into());
    p.push("537".into());
    p.push("420".into());
    p.push("45".into());
    p.push("253".into());
    p.push("593".into());
    p.push("20".into());
    p.push("503".into());
    p.push("240".into());
    p.push("291".into());
    p.push("372".into());
    p.push("251".into());
    p.push("298".into());
    p.push("679".into());
    p.push("358".into());
    p.push("33".into());
    p.push("594".into());
    p.push("689".into());
    p.push("241".into());
    p.push("220".into());
    p.push("995".into());
    p.push("49".into());
    p.push("233".into());
    p.push("350".into());
    p.push("30".into());
    p.push("299".into());
    p.push("590".into());
    p.push("502".into());
    p.push("224".into());
    p.push("245".into());
    p.push("595".into());
    p.push("509".into());
    p.push("504".into());
    p.push("36".into());
    p.push("354".into());
    p.push("91".into());
    p.push("62".into());
    p.push("964".into());
    p.push("353".into());
    p.push("972".into());
    p.push("39".into());
    p.push("81".into());
    p.push("962".into());
    p.push("254".into());
    p.push("686".into());
    p.push("965".into());
    p.push("996".into());
    p.push("371".into());
    p.push("961".into());
    p.push("266".into());
    p.push("231".into());
    p.push("423".into());
    p.push("370".into());
    p.push("352".into());
    p.push("261".into());
    p.push("265".into());
    p.push("60".into());
    p.push("960".into());
    p.push("223".into());
    p.push("356".into());
    p.push("692".into());
    p.push("596".into());
    p.push("222".into());
    p.push("230".into());
    p.push("262".into());
    p.push("52".into());
    p.push("377".into());
    p.push("976".into());
    p.push("382".into());
    p.push("1664".into());
    p.push("212".into());
    p.push("95".into());
    p.push("264".into());
    p.push("674".into());
    p.push("977".into());
    p.push("31".into());
    p.push("599".into());
    p.push("687".into());
    p.push("64".into());
    p.push("505".into());
    p.push("227".into());
    p.push("234".into());
    p.push("683".into());
    p.push("672".into());
    p.push("47".into());
    p.push("968".into());
    p.push("92".into());
    p.push("680".into());
    p.push("507".into());
    p.push("675".into());
    p.push("595".into());
    p.push("51".into());
    p.push("63".into());
    p.push("48".into());
    p.push("351".into());
    p.push("974".into());
    p.push("40".into());
    p.push("250".into());
    p.push("685".into());
    p.push("378".into());
    p.push("966".into());
    p.push("221".into());
    p.push("381".into());
    p.push("248".into());
    p.push("232".into());
    p.push("65".into());
    p.push("421".into());
    p.push("386".into());
    p.push("677".into());
    p.push("27".into());
    p.push("500".into());
    p.push("34".into());
    p.push("94".into());
    p.push("249".into());
    p.push("597".into());
    p.push("268".into());
    p.push("46".into());
    p.push("41".into());
    p.push("992".into());
    p.push("66".into());
    p.push("228".into());
    p.push("690".into());
    p.push("676".into());
    p.push("216".into());
    p.push("90".into());
    p.push("993".into());
    p.push("688".into());
    p.push("256".into());
    p.push("380".into());
    p.push("971".into());
    p.push("44".into());
    p.push("1".into());
    p.push("598".into());
    p.push("998".into());
    p.push("678".into());
    p.push("681".into());
    p.push("967".into());
    p.push("260".into());
    p.push("263".into());
    p.push("591".into());
    p.push("673".into());
    p.push("61".into());
    p.push("243".into());
    p.push("225".into());
    p.push("500".into());
    p.push("44".into());
    p.push("379".into());
    p.push("852".into());
    p.push("98".into());
    p.push("44".into());
    p.push("44".into());
    p.push("850".into());
    p.push("82".into());
    p.push("856".into());
    p.push("218".into());
    p.push("853".into());
    p.push("389".into());
    p.push("691".into());
    p.push("373".into());
    p.push("258".into());
    p.push("970".into());
    p.push("872".into());
    p.push("262".into());
    p.push("7".into());
    p.push("590".into());
    p.push("290".into());
    p.push("590".into());
    p.push("508".into());
    p.push("239".into());
    p.push("252".into());
    p.push("47".into());
    p.push("963".into());
    p.push("886".into());
    p.push("255".into());
    p.push("670".into());
    p.push("58".into());
    p.push("84".into());
    // normalis number
    let mut startpoint=0;
    if phonenumber[0]==b'0' && phonenumber[1]==b'0' {
        startpoint=2;
    }
    if phonenumber[0]==b'+' {
        startpoint=1;
    }
    // create vec for comparison
    let mut pc3:Vec<u8>= Vec::new();
    pc3.push(phonenumber[startpoint]);
    pc3.push(phonenumber[startpoint+1]);
    pc3.push(phonenumber[startpoint+2]);
    let mut pc2:Vec<u8>= Vec::new();
    pc2.push(phonenumber[startpoint]);
    pc2.push(phonenumber[startpoint+1]);
    let mut pc1:Vec<u8>= Vec::new();
    pc1.push(phonenumber[startpoint]);
    let mut valid=false;
    for xp in p {
        if xp==pc3 || xp==pc2 || xp==pc1 {
            valid =true;
        }
    }
    valid
}
