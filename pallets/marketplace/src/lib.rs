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
    }
}

// We generate events to inform the users of succesfully actions.
decl_event!(
    pub enum Event<T>
    where
        AccountId = <T as frame_system::Config>::AccountId,
    {
        MarketPlaceDepartmentCreated(u32, Vec<u8>), // New department created
        MarketPlaceDepartmentDestroyed(u32),        // Department has been destroyed/removed
        MarketPlaceSellerCreated(AccountId, Vec<u8>), // New seller has been created
        MarketPlaceCategoryCreated(u32, u32, Vec<u8>), // New producct category has been created
        MarketPlaceCategoryDestroyed(u32, u32),     // Product category has been destroyed
        MarketPlaceIsoCountryCreated(Vec<u8>, Vec<u8>), // New Iso contry code has been created
        MarketPlaceIsoCountryDestroyed(Vec<u8>),    // Iso contry code has been destroyed
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
        pub fn create_seller(origin, configuration: Vec<u8>) -> dispatch::DispatchResult {
            // check the request is signed
            let sender = ensure_signed(origin)?;
            //check configuration length
            ensure!(configuration.len() > 12, Error::<T>::ConfigurationTooShort);
            ensure!(configuration.len() < 8192, Error::<T>::ConfigurationTooLong);
            ensure!(Sellers::<T>::contains_key(&sender)==false, Error::<T>::SellerAlreadyPresent);
            // check json validity
            let js=configuration.clone();
            ensure!(json_check_validity(js),Error::<T>::InvalidJson);
            // Insert configuration of the impact action
            //ImpactActions::insert(uid,configuration.clone());
            // Generate event
            Self::deposit_event(RawEvent::MarketPlaceSellerCreated(sender,configuration));
            // Return a successful DispatchResult
            Ok(())
        }
        /// Create a new Iso country
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
